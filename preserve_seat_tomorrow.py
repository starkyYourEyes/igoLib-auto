import functools
import json
import random
import time
import websockets
from keep_reserve import *
import requests
from keep_session import *
from lib_configs import *
import schedule
import my_email
from threading import Thread
import ssl
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
    with open('init_conf.json', 'r', encoding='utf-8') as fp:
        usr_list = json.loads(fp.read())['users']
    print('============================================================================')
    usr_list = list(filter(lambda x: x['cookie'] != "", usr_list))
    for usr in usr_list:
        usr['cookie'] = usr['cookie'].strip('\r\n')
        if usr['cookie'] != '':
            pre_header['Cookie'] = usr['cookie']
            usr_info = requests.post(url=url, headers=pre_header, json=params_index, verify=False).json()
            ct_usr = usr_info['data']['userAuth']['currentUser']
            print('hello,', '%s' % ct_usr['user_student_name'], end='; ')
            print(ct_usr['sch']['sch_name'] + '|' + ct_usr['user_student_no'], end='; ')
            print('明日预约的时间:', time_update(usr['pre_reserve_time']).split()[1])
    print('============================================================================')


def seat_save(open_time, session):
    # for henan # ?????
    if time.time() - open_time >= 8:
        session.post(
            url=url,
            headers=pre_header,
            json=data_lib_chosen,  # libLayout
            verify=False
        )
    queue_end = time.time()
    try:
        for seat in the_seat_chosen:
            params_confirm_seat['variables']['key'] = seat + '.'
            text_save = session.post(  # 抢座的post请求，core code
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

            print('⛳本次排队消耗时间:', queue_end - open_time)
            print('🌻抢座过程消耗时间:', save_end - queue_end)
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


async def queue_pass_websockets(open_time, session):
    """
    經過實驗，知道了，即使沒到明日預約開始的時間，仍然可以連接服務器，所以可以省下來連接服務器的時間
    由此建立第四種方法
    """
    # 创建一个 SSL 上下文并指定协议版本
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    success_pre_reserve = False  # 抢座成功与否的标志
    async with websockets.connect("wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
                                  extra_headers=queue_header_for_websockets,
                                  ssl=ssl_context) as websocket:
        # 重要！如果不是放在常用座位，需要先请求对应的阅览室的所有座位，libLayout！！
        # 将访问对应阅览室的请求放在前面，效果一样，缩短抢座所需时间 0.2~0.3s -> 0.05s
        """如果排队的时间比较短，可以起到上述的作用，排队时间比较长 比如>30s，则需要在save的时候再重新执行"""
        session.post(
            url=url,
            headers=pre_header,
            json=data_lib_chosen,  # libLayout
            verify=False
        )
        # 在搶座開始前0.8s就對服務器開始狂轟濫炸???😝
        start_queue_time = open_time - 0.8
        end_queue_time = open_time + 0.1
        print('💥距离开始还有:', open_time - time.time())

        """时间戳转格式%Y-%m-%d %H:%M:%S"""
        time_local = time.localtime(open_time)  # 转换成localtime
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)  # 转换成新的时间格式(2016-05-05 20:28:54)
        print(dt, '的时间戳为：', open_time)
        # 记录发送的msg的次数（有多少次发送就有多少次返回？）
        cnt_sent, cnt_recv, save_round = 0, 0, 0
        while True:  # 外循环控制时间
            if time.time() >= start_queue_time:
                while True:  # 内循环控制websocket通信，直到收到排队成功的消息
                    try:
                        while start_queue_time <= time.time() <= end_queue_time:
                            await websocket.send('{"ns":"prereserve/queue","msg":""}')
                            cnt_sent += 1
                            print(cnt_sent, '>>> msg1', time.time())
                            # sleep or not？
                            time.sleep(0.01)
                        else:
                            # 没到设定的开始排队的时间，不不要开始，while不成立或者while执行结束就会执行else
                            if time.time() >= end_queue_time:
                                await websocket.send('{"ns":"prereserve/queue","msg":""}')
                                cnt_sent += 1
                                print(cnt_sent, '>>> msg2', time.time())
                        # 把上面发送的消息所收到的返回接收完
                        while cnt_sent > 0:
                            ans = await websocket.recv()
                            cnt_recv += 1
                            cnt_sent -= 1
                            print(cnt_recv, '<<<', time.time(), ans)
                            if ans.__contains__('u6392'):
                                """\u6392排好队的返回， \u6210已经抢完座的返回"""
                                success_pre_reserve = seat_save(open_time, session)
                                save_round += 1
                                print('🎵round', save_round, 'end')
                                break
                        if success_pre_reserve or save_round >= 3:  # 抢座成功或者抢座超过3轮直接退出
                            return
                    except Exception as e:
                        print(e)
                        if time.time() - open_time >= 40:  # 保证程序退出
                            break
                        time.sleep(0.8)

                break  # 跳出外层循环

    if not success_pre_reserve:
        my_email.goLib_email_info('fail')


def preserve_tomorrow(session, usr: dict):
    cookie = usr['cookie']
    queue_header_for_websockets['Cookie'] = cookie  # websockets的请求头的形式 => dict
    pre_header['Cookie'] = cookie  # http请求的请求头
    # 更新为当日抢座时间,open_time -> 时间戳
    open_time = time.mktime(time.strptime(time_update(usr['pre_reserve_time']), "%Y-%m-%d %H:%M:%S"))
    print('🙏明日预约初始化完成！')
    print('当前时间', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), end=', ')
    print('还有%f秒开始' % (open_time - time.time()))

    start_preserve_time = open_time - 5  # 用一个变量保存开始的时间，避免每一次的循环中都要计算open_time - 5
    while True:
        if time.time() >= start_preserve_time:  # 提前5s开始，建立socket，然后直接排队
            """websockets, asyncio, 2s ahead of the lib websocket server start"""
            asyncio.run(queue_pass_websockets(open_time, session))
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
    # 每天22：29准时退座
    schedule.every().day.at("21:59:30").do(run_thread, param_dict={
        'func': withdraw_seat,
        'session': session,
        # 暂时----只给自己自动退座
        'usr': usr_list[0]
    })
    # 20:00开始抢座的
    schedule.every().day.at("20:59:50").do(run_thread, param_dict={
        'func': preserve_tomorrow,
        'session': session,
        # 暂时---只给自己自动抢座
        'usr': usr_list[0]
    })

    while True:
        schedule.run_pending()
        time.sleep(1)
