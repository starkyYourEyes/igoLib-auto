import functools
import schedule
from threading import Thread
from my_socket import *
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
        """把座位name改为座位key，顺序执行，不需要考虑线程间的影响"""
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
    print(user.name, '本次排队消耗时间:', queue_end - open_time)
    if time.time() - open_time >= 8:  # for henan # ?????
        my_libLayout_operation = copy.deepcopy(libLayout_operation)
        my_libLayout_operation['variables']['libId'] = user.lib_id
        user.session.post(
            url=url,
            json=my_libLayout_operation,  # libLayout
            verify=False
        )
        print('time in libLayout operation:', time.time() - queue_end)
    try:
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
            print(user.name, '抢座过程消耗时间:', save_end - queue_end)
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
                    print(f'{user.name}, 获取每日诗词失败或发送邮件失败。。。')
                return True
            else:
                time.sleep(1)
    except Exception as e:
        time.sleep(0.3)
        print(e)
    return False


def preserve_tomorrow(user: User):
    # 更新为当日抢座时间,open_time -> 时间戳
    open_time = time.mktime(
        time.strptime(time_update(user.pre_reserve_time), "%Y-%m-%d %H:%M:%S"))
    print(f'🙏{user.name} 明日预约初始化完成！')
    print('当前时间', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), end=', ')
    print(f'{user.name} 还有%f秒开始' % (open_time - time.time()))
    start_preserve_time = open_time - 5
    save_success = False
    save_round = 0
    cnt_except = 0
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    while True:
        if time.time() >= start_preserve_time:  # 提前4s开始，建立socket，然后直接排队
            my_queue_header = copy.deepcopy(queue_header)
            try:
                # 在抢座开始之前就已经建立好了这个socket，节省时间
                my_queue_header.append(('Cookie', User.cookie_dict_to_str_with_equal(
                    requests.utils.dict_from_cookiejar(user.session.cookies))))
                ws = CG_Client(
                    url="wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
                    headers=my_queue_header,
                    ssl_options={
                        "cert_reqs": ssl.CERT_NONE
                    }
                )
                # ws.open_time = open_time
                ws.queue_start_time = open_time - 0.6
                ws.queue_end_time = open_time + 0.1
                ws.user_name = user.name
                my_libLayout_operation = copy.deepcopy(libLayout_operation)
                my_libLayout_operation['variables']['libId'] = user.lib_id
                print(f"name:{user.name}, lib_id:{user.lib_id}, seats:{user.seats}")
                user.session.post(
                    url=url,
                    json=my_libLayout_operation,  # libLayout
                    verify=False
                )
                print(user.name, '明日预约距离开始还有:', open_time - time.time())
                ws.connect()
                ws.run_forever()
                save_round += 1
                save_success = seat_save(open_time, user)
            except Exception as e:
                cnt_except += 1
                print(e)
                time.sleep(0.3)
            finally:
                while my_queue_header[-1][0] == 'Cookie':
                    my_queue_header.pop()
                if save_success or save_round >= 3 or cnt_except >= 8:
                    break
    print(user.name, time_update().split(' ')[0] + "的抢座结束！")

    if not save_success:
        my_email.goLib_email_info('fail', receiver='2389372927@qq.com')


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

    schedule.every(3 * 60 + random.randint(-60, 60)).seconds.do(run_thread, param_dict={
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