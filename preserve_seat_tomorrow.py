import copy
import functools
import ssl
import time
import websockets
import schedule
from threading import Thread
import asyncio
from User import *

user_list = []


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
    global user_list
    requests.packages.urllib3.disable_warnings()
    with open('init_conf.json', 'r', encoding='utf-8') as fp:
        list_user = json.loads(fp.read())['users']
    list_user = list(filter(lambda x: x['cookie'] != "", list_user))
    # 每一个user有一个自己的session -> session会自动更新cookie...
    for usr in list_user:
        usr['cookie'] = usr['cookie'].strip('\r\n')
        user_list.append(User(usr))
    print('============================================================================')
    for user in user_list:
        """
        把座位name改为座位key，这里是顺序执行的（initialization函数不涉及多线程）
        不需要考虑各个线程修改libLayout的影响。。
        """
        libLayout_operation['variables']['libId'] = user.lib_id
        assert user.session is not None and user.cookie is not None and user.cookie != ''
        all_seats = user.session.post(
            url=url, json=libLayout_operation, verify=False
        ).json()
        assert all_seats is not None
        assert all_seats['data']['userAuth'] is not None
        all_seats = all_seats['data']['userAuth']['prereserve']['libLayout']['seats']
        my_seat_list = []
        for my_seat in user.seats:
            for seat in all_seats:
                if seat['name'] == my_seat:
                    my_seat_list.append(seat['key'])
                    break
        user.seats = my_seat_list
        user_info = user.session.post(
            url=url, json=index_operation, verify=False
        ).json()
        assert user_info['data']['userAuth'] is not None
        ct_user = user_info['data']['userAuth']['currentUser']
        print('hello,', '%s' % ct_user['user_student_name'], end='; ')
        print(ct_user['sch']['sch_name'] + '|' + ct_user['user_student_no'], end='; ')
        print('明日预约的时间:', time_update(user.pre_reserve_time).split()[1])
        print(user)
    print('============================================================================')


def seat_save(open_time, user):
    queue_end = time.time()
    print(f'{user.name} 本次排队消耗时间:', queue_end - open_time)
    if time.time() - open_time >= 5:  # for henan # ?????
        my_libLayout_operation = copy.deepcopy(libLayout_operation)
        my_libLayout_operation['variables']['libId'] = user.lib_id
        user.session.post(
            url=url,
            json=my_libLayout_operation,  # libLayout
            verify=False
        )
        print(f'{user.name} time in libLayout_operation:', time.time() - queue_end)
    try:
        # save_operation['variables']['libid'] = user.lib_id
        my_save_operation = copy.deepcopy(save_operation)
        my_save_operation['variables']['libid'] = user.lib_id
        for seat in user.seats:
            my_save_operation['variables']['key'] = seat + '.'
            text_save = user.session.post(  # 抢座的post请求，core code
                url=url,
                json=my_save_operation,  # save
                verify=False
            ).text
            save_end = time.time()
            print('save end:', save_end)
            text_res = user.session.post(
                url=url,
                json=prereserve_operation,  # prereserve
                verify=False
            ).text
            print(f'{user.name} 抢座过程消耗时间:{save_end - queue_end}')
            print(time.ctime(), 'pre reserve:',
                  str(text_res).encode('utf-8').decode('unicode_escape'))
            print(time.ctime(), 'save       :',
                  str(text_save).encode('utf-8').decode('unicode_escape'))
            if text_res.count('user_mobile'):
                print(f"😍恭喜 {user.name}！明日预约成功！记得早起")  # 抢座成功就返回
                try:
                    my_email.goLib_email_info('success', json.loads(text_res), user.email)
                except Exception as e:
                    print(e)
                    print(f'{user.name} 获取每日诗词失败或发送邮件失败。。。')
                return True
            else:
                time.sleep(1)
    except Exception as e:
        time.sleep(0.3)
        print(e)
    return False


async def queue_pass_websockets(open_time, user):
    """經過實驗，知道了，即使沒到明日預約開始的時間，仍然可以連接服務器，所以可以省下來連接服務器的時間"""
    # 创建一个 SSL 上下文并指定协议版本
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    my_queue_header = copy.deepcopy(queue_header_for_websockets)
    my_queue_header['Cookie'] = User.cookie_dict_to_str_with_equal(
        requests.utils.dict_from_cookiejar(user.session.cookies)
    )
    # queue_header_for_websockets['Cookie'] = user.cookie
    success_pre_reserve = False  # 抢座成功与否的标志
    async with websockets.connect("wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
                                  extra_headers=my_queue_header,
                                  ssl=ssl_context) as websocket:
        # 重要！如果不是放在常用座位，需要先请求对应的阅览室的所有座位，libLayout！！
        # 将访问对应阅览室的请求放在前面，效果一样，缩短抢座所需时间 0.2~0.3s -> 0.05s
        my_libLayout_operation = copy.deepcopy(libLayout_operation)
        my_libLayout_operation['variables']['libId'] = user.lib_id
        print('name and seats:', user.name, user.seats)
        """如果排队的时间比较短，可以起到上述的作用，排队时间比较长 比如>10s，则需要在save的时候再重新执行(maybe"""
        user.session.post(
            url=url,
            json=my_libLayout_operation,  # libLayout
            verify=False
        )
        # 在搶座開始前0.5s就對服務器開始狂轟濫炸???😝
        start_queue_time = open_time - 0.5
        end_queue_time = open_time + 0.1
        print(f'{user.name} 距离开始还有:', open_time - time.time())
        """时间戳转格式%Y-%m-%d %H:%M:%S"""
        time_local = time.localtime(open_time)  # 转换成localtime
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)  # 转换成新的时间格式(2016-05-05 20:28:54)
        # print(dt, '的时间戳为：', open_time)
        # 记录发送的msg的次数（有多少次发送就有多少次返回？）
        cnt_recv, save_round = 0, 0
        name = user.name
        while True:  # 外循环控制时间
            if time.time() >= start_queue_time:
                while True:  # 内循环控制websocket通信，直到收到排队成功的消息
                    try:
                        await websocket.send('{"ns":"prereserve/queue","msg":""}')
                        print(name, '>>> msg', time.time())
                        ans = await websocket.recv()
                        cnt_recv += 1
                        print(cnt_recv, f'{name} <<<', ans, time.time())
                        if ans.__contains__('u6392'):
                            """\u6392排好队的返回， \u6210已经抢完座的返回"""
                            success_pre_reserve = seat_save(open_time, user)
                            save_round += 1
                            print('🎵round', save_round, 'end')
                        elif ans.__contains__('u6210'):
                            print(ans)
                        elif ans.find('u83b7') != -1:  # 获取用户信息失败！？
                            my_email.goLib_email_info('error')

                        if success_pre_reserve or save_round >= 3 or cnt_recv >= 185:  # 抢座成功或者抢座超过3轮直接退出
                            break
                    except Exception as e:
                        print(e)
                        if time.time() - open_time >= 90 or save_round >= 5:  # 保证程序退出
                            break
                        time.sleep(0.8)
                break  # 跳出外层循环
    if not success_pre_reserve:
        my_email.goLib_email_info('fail', receiver='2389372927@qq.com')


def preserve_tomorrow(user: User):
    # 更新为当日抢座时间,open_time -> 时间戳
    open_time = time.mktime(
        time.strptime(time_update(user.pre_reserve_time), "%Y-%m-%d %H:%M:%S"))
    print(f'🙏{user.name} 明日预约初始化完成！')
    print('当前时间', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), end=', ')
    print('还有%f秒开始' % (open_time - time.time()))
    start_preserve_time = open_time - 4
    while True:
        if time.time() >= start_preserve_time:  # 提前4s开始，建立socket，然后直接排队
            """websockets, asyncio, 4s ahead of the lib websocket server start"""
            asyncio.run(queue_pass_websockets(open_time, user))
            break
    print(user.name, time_update(user.pre_reserve_time).split(' ')[0] + "的抢座结束！")


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
    assert len(user_list) > 0
    for user in user_list:  # 检查
        assert user.cookie is not None and user.cookie != ''
        assert user.session is not None
    print('🌠我去图书馆程序，启动！🌠 ', time.ctime())
    print(f"currently {len(user_list)} users active")
    User.keep_session(user_list)  # 先进行一次session刷新，避免开始的三五分钟内失效
    schedule.every(4 * 60 + random.randint(-60, 60)).seconds.do(run_thread, param_dict={
        'func': User.keep_session,  # 每3~5分钟刷新cookie, 保活session
        'user_list': user_list
    })
    for user in user_list:  # 每天按User.close_lib_time准时退座
        schedule.every().day.at(user.close_lib_time).do(run_thread, param_dict={
            'func': User.withdraw_seat,
            'user': user
        })
    for user in user_list:  # 20:00开始抢座的，需要提前设置10s or so
        open_time = time.mktime(  # 先获得一下时间，%H:%M:%S,填入schedule中
            time.strptime(time_update(user.pre_reserve_time), "%Y-%m-%d %H:%M:%S")
        ) - 10
        time_local = time.localtime(open_time)  # 转换成localtime
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local).split()[1]  # 转换成新的时间格式(2016-05-05 20:28:54)
        # print(user.pre_reserve_time), print(open_time), print(dt)
        schedule.every().day.at(dt).do(run_thread, param_dict={
            'func': preserve_tomorrow,
            'user': user
        })
    while True:
        schedule.run_pending()
        time.sleep(1)

