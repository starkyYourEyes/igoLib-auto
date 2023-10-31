import functools
import time

import websockets
from keep_reserve import *
from keep_session import *
from lib_configs import *
import schedule
import my_email
from threading import Thread
from my_socket import *
import asyncio

usr_list = []


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                my_email.goLib_email_info('error')
                if cancel_on_failure:
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator


def initialization():
    """讀取各個用戶的cookie，直接保存到内存"""
    global usr_list
    requests.packages.urllib3.disable_warnings()
    with open('../init_conf.json', 'r', encoding='utf-8') as fp:
        usr_list = json.loads(fp.read())['users']
    usr_list = list(filter(lambda x: x['cookie'] != "", usr_list))

    print('============================================================================')
    for usr in usr_list:
        usr['cookie'] = usr['cookie'].strip('\r\n')
        pre_header['Cookie'] = usr['cookie']  # 注意cookie
        """把座位name改为座位key"""
        data_lib_chosen['variables']['libId'] = usr['lib_id']
        all_seats = requests.post(
            url=url, headers=pre_header, json=data_lib_chosen, verify=False
        ).json()
        assert all_seats is not None
        assert all_seats['data']['userAuth'] is not None

        all_seats = all_seats['data']['userAuth']['prereserve']['libLayout']['seats']
        my_seat_list = []
        for my_seat in usr['seats']:
            for seat in all_seats:
                if seat['name'] == my_seat:
                    my_seat_list.append(seat['key'])
                    break
        # print(usr)
        usr['seats'] = my_seat_list
        usr_info = requests.post(url=url, headers=pre_header, json=params_index, verify=False).json()
        ct_usr = usr_info['data']['userAuth']['currentUser']
        print('hello,', '%s' % ct_usr['user_student_name'], end='; ')
        print(ct_usr['sch']['sch_name'] + '|' + ct_usr['user_student_no'], end='; ')
        print('明日预约的时间:', time_update(usr['pre_reserve_time']).split()[1])
        # print(usr)
    print('============================================================================')


def seat_save(open_time, session, usr):

    # pppppppp
    time.sleep(15)

    # for henan # ?????
    pre_header['Cookie'] = usr['cookie']
    print(usr['seats'])

    # if time.time() - (open_time - 4) >= 0:
    #     eee = time.time()
    #     print(eee)
    #     session.post(
    #         url=url,
    #         headers=pre_header,
    #         json=data_lib_chosen,  # libLayout
    #         verify=False
    #     )
    #     print('time in libLaylout:', time.time() - eee)

    try:
        for _ in range(3):
            for seat in usr['seats']:
                params_confirm_seat['variables']['key'] = seat + '.'
                text_save = session.post(  # 抢座的post请求
                    url=url,
                    headers=pre_header,
                    json=params_confirm_seat,  # save
                    verify=False
                ).text
                save_end = time.time()
                text_res = session.post(
                    url=url,
                    headers=pre_header,
                    json=params_confirm_seat_info,  # prereserve
                    verify=False
                ).text

                print(time.ctime(), 'pre reserve:',
                      str(text_res).encode('utf-8').decode('unicode_escape'))
                print(time.ctime(), 'save       :',
                      str(text_save).encode('utf-8').decode('unicode_escape'))
                if text_res.count('user_mobile'):
                    print("🐮恭喜！ 明日预约成功！记得早起🍺")  # 抢座成功就返回
                    try:
                        my_email.goLib_email_info('success', json.loads(text_res))
                    except Exception as e:
                        print(e)
                        print('获取每日诗词失败或发送邮件失败。。。')
                    return True
                else:
                    time.sleep(1)
    except Exception as e:
        time.sleep(0.3)
        print(e)
    return False



def preserve_tomorrow(session, usr: dict):
    # cookie = usr['cookie']
    # queue_header_for_websockets['Cookie'] = cookie  # websockets的请求头的形式 => dict
    # pre_header['Cookie'] = cookie  # http请求的请求头
    params_confirm_seat['variables']['libid'] = usr['lib_id']
    # 更新为当日抢座时间,open_time -> 时间戳

    open_time = time.mktime(time.strptime(time_update(usr['pre_reserve_time']), "%Y-%m-%d %H:%M:%S"))
    print(time.time(), open_time)
    print('🙏明日预约初始化完成！')
    print('当前时间', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), end=', ')
    print('还有%f秒开始' % (open_time - time.time()))

    start_preserve_time = open_time - 5  # 用一个变量保存开始的时间，避免每一次的循环中都要计算open_time - 5
    while True:
        if time.time() >= start_preserve_time:  # 提前5s开始，建立socket，然后直接排队
            """websockets, asyncio, 5s ahead of the lib websocket server start"""
            # 在抢座开始之前就已经建立好了这个socket，节省时间
            queue_header.append(('Cookie', usr['cookie']))
            ws = CG_Client(
                url="wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
                headers=queue_header
                # ssl_options={}
            )

            ws.queue_start_time = open_time - 0.4
            ws.open_time = open_time
            ws.queue_end_time = open_time + 0.1
            ws.name = usr['name']
            # 没到时间也可连接到服务器， connect的时候即开始收发消息
            ws.connect()
            # run_forever是一个阻塞方法，用于保持WebSocket连接的活动状态并处理接收和发送消息。
            ws.run_forever()

            seat_save(open_time, session, usr)
            # queue_pass_websockets(open_time, session, usr)
            break
    # 搶座結束了
    print(usr['name'], time_update(usr['pre_reserve_time']).split(' ')[0] + "的抢座结束！")


@catch_exceptions(cancel_on_failure=True)
def run_thread(param_dict):
    """
    schedule每一次重新運行的時候，會保留上一次的更改，包括schedule所執行的函數的形參的變化，都會一直保留……
    python不定參數 reference:https://blog.csdn.net/cadi2011/article/details/84871401
    """
    Thread(
        target=param_dict['func'],
        # 过滤掉原参数字典中的键func
        kwargs=dict(filter(lambda x: x[0] != 'func', param_dict.items()))
    ).start()


if __name__ == '__main__':
    initialization()
    print('currently', len(usr_list), 'users active')
    # session 对象 -> 保活
    session = requests.session()
    print('🌠我去图书馆程序，启动！🌠 ', time.ctime())
    keep_session_newest(session=session, usr_list=usr_list)  # 先进行一次session初始化设置，
    # 每3~5分钟刷新cookie, 保活session
    schedule.every(4 * 60 + random.randint(-60, 60)).seconds.do(run_thread, param_dict={
        'func': keep_session_newest,
        'session': session,
        'usr_list': usr_list
    })
    # 每天按usr['close_lib_time']准时退座
    for usr in usr_list:
        schedule.every().day.at(usr['close_lib_time']).do(run_thread, param_dict={
            'func': withdraw_seat,
            'session': session,
            'usr': usr
        })
    # 20:00开始抢座的，需要提前设置10s or so
    for usr in usr_list:
        # 先获得一下时间，%H:%M:%S,填入schedule中
        open_time = time.mktime(
            time.strptime(time_update(usr['pre_reserve_time']), "%Y-%m-%d %H:%M:%S")
        ) - 10
        time_local = time.localtime(open_time)  # 转换成localtime
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local).split()[1]  # 转换成新的时间格式(2016-05-05 20:28:54)
        # print(usr['pre_reserve_time']), print(open_time), print(dt)

        schedule.every().day.at(dt).do(run_thread, param_dict={
            'func': preserve_tomorrow,
            'session': session,
            'usr': usr
        })
    while True:
        schedule.run_pending()
        time.sleep(1)
