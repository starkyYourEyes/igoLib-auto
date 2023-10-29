import functools
import json
import random
import time
import websockets
from keep_reserve import *
import websocket
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
# basic configs
seat_key, lib_id = the_seat_chosen[0], the_lib_chosen[0]
# save
params_confirm_seat = {
    "operationName": "save",
    "query": "mutation save($key: String!, $libid: Int!, $captchaCode: String, $captcha: String) {\n userAuth {\n "
             "prereserve {\n save(key: $key, libId: $libid, captcha: $captcha, captchaCode: $captchaCode)\n }\n }\n}",
    "variables": {
        # 这里的"key"：如果不是常用座位，需要在最后面加一个 '.'
        "key": seat_key + '.',
        "libid": lib_id,
        "captchaCode": "",
        "captcha": ""
    }
}
# libLayout
data_lib_chosen = {
    "operationName": "libLayout",
    "query": "query libLayout($libId: Int!) {\n userAuth {\n prereserve {\n libLayout(libId: $libId) {\n max_x\n "
             "max_y\n seats_booking\n seats_total\n seats_used\n seats {\n key\n name\n seat_status\n status\n type\n "
             "x\n y\n }\n }\n }\n }\n}",
    "variables": {
        "libId": lib_id
    }
}
# prereserve
params_confirm_seat_info = {"operationName": "prereserve",
                            "query": "query prereserve {\n userAuth {\n prereserve {\n prereserve {\n day\n lib_id\n "
                                     "seat_key\n seat_name\n is_used\n user_mobile\n id\n lib_name\n }\n }\n }\n}"}

url = 'https://wechat.v2.traceint.com/index.php/graphql/'

params_index = {
    "operationName": "index",
    "query": "query index($pos: String!, $param: [hash]) {\n userAuth {\n oftenseat {\n list {\n id\n info\n lib_id\n "
             "seat_key\n status\n }\n }\n message {\n new(from: \"system\") {\n has\n from_user\n title\n num\n }\n "
             "indexMsg {\n message_id\n title\n content\n isread\n isused\n from_user\n create_time\n }\n }\n reserve "
             "{\n reserve {\n token\n status\n user_id\n user_nick\n sch_name\n lib_id\n lib_name\n lib_floor\n "
             "seat_key\n seat_name\n date\n exp_date\n exp_date_str\n validate_date\n hold_date\n diff\n diff_str\n "
             "mark_source\n isRecordUser\n isChooseSeat\n isRecord\n mistakeNum\n openTime\n threshold\n daynum\n "
             "mistakeNum\n closeTime\n timerange\n forbidQrValid\n renewTimeNext\n forbidRenewTime\n "
             "forbidWechatCancle\n }\n getSToken\n }\n currentUser {\n user_id\n user_nick\n user_mobile\n user_sex\n "
             "user_sch_id\n user_sch\n user_last_login\n user_avatar(size: MIDDLE)\n user_adate\n user_student_no\n "
             "user_student_name\n area_name\n user_deny {\n deny_deadline\n }\n sch {\n sch_id\n sch_name\n "
             "activityUrl\n isShowCommon\n isBusy\n }\n }\n }\n ad(pos: $pos, param: $param) {\n name\n pic\n url\n "
             "}\n}",
    "variables": {
        "pos": "App-首页"
    }
}

pre_header = {
    'Host': 'wechat.v2.traceint.com',
    'Connection': 'keep-alive',
    'Content-Length': '309',
    'App-Version': '2.0.14',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 '
                  'Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090719) '
                  'XWEB/8391 Flue',
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Origin': 'https://web.traceint.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://web.traceint.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh',
    # 'Cookie': cookieStr
}


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
    """
    讀取各個用戶的cookie，直接保存到内存
    :return:
    """
    global usr_list
    with open('init_conf.json', 'r', encoding='utf-8') as fp:
        usr_list = json.loads(fp.read())['cookies']
    for usr in usr_list:
        usr['cookie'] = usr['cookie'].strip('\r\n')

    pre_header['Cookie'] = usr_list[0]['cookie']
    usr_info = requests.post(url=url, headers=pre_header, json=params_index, verify=False).json()
    ct_usr = usr_info['data']['userAuth']['currentUser']
    # print('您好', end='!')
    print('您好！')
    # print(ct_usr['user_student_name'], end='-')
    # print(ct_usr['user_student_no'], end='-')
    # print(ct_usr['sch']['sch_name'])
    print('姓名:', ct_usr['user_student_name'])
    print('学号:', ct_usr['user_student_no'])
    print('学校:', ct_usr['sch']['sch_name'])


def preserve_tomorrow(session, usr: dict):
    # 标志抢座成功 or 失败
    preserve_success = False
    # 更新cookie
    cookie = usr['cookie']
    # http请求的请求头
    pre_header['Cookie'] = cookie
    # ws4py的请求头的形式 => tuples list
    queue_header.append(('Cookie', cookie))

    # 更新为当日抢座时间,open_time -> 时间戳
    open_time = time.mktime(time.strptime(time_update(), "%Y-%m-%d %H:%M:%S"))
    print('🙏明日预约初始化完成！')
    print('当前时间', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), end=', ')
    print('还有%f秒开始' % (open_time - time.time()))

    # 用一个变量保存开始的时间，避免每一次的循环中都要计算open_time - 5
    start_preserve_time = open_time - 5
    while True:
        if time.time() >= start_preserve_time:  # 提前5s开始，建立socket，然后直接排队
            # 重要！如果不是放在常用座位，需要先请求对应的阅览室的所有座位，libLayout！！
            # 将访问对应阅览室的请求放在前面，效果一样，缩短抢座所需时间 0.2~0.3s -> 0.05s
            session.post(
                url=url,
                headers=pre_header,
                json=data_lib_chosen,  # libLayout
                verify=False
            )
            try:
                # 在抢座开始之前就已经建立好了这个socket，节省时间
                ws = CG_Client(
                    url="wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
                    headers=queue_header
                    # ssl_options={}
                )
                # 将时间控制放到了websocket类内部
                ws.open_time = open_time
                ws.queue_start_time = open_time - 1
                ws.queue_end_time = open_time + 0.1
                # QUEUE
                # 没到时间也可连接到服务器， connect的时候即开始收发消息
                ws.connect()
                # run_forever是一个阻塞方法，用于保持WebSocket连接的活动状态并处理接收和发送消息。
                ws.run_forever()
                queue_end = time.time()
                for seat in the_seat_chosen:
                    # 抢座的post请求，core code
                    params_confirm_seat['variables']['key'] = seat + '.'
                    # print(params_confirm_seat)
                    text_save = session.post(
                        url=url,
                        headers=pre_header,
                        json=params_confirm_seat,  # save
                        verify=False
                    ).text
                    save_end = time.time()
                    print('🚒save ==> ok!')
                    text_res = session.post(
                        url=url,
                        headers=pre_header,
                        json=params_confirm_seat_info,  # prereserve
                        verify=False
                    ).text
                    print('⛳本次排队消耗时间:', queue_end - open_time)
                    print('🌻抢座过程消耗时间:', save_end - queue_end)
                    print('pre reserve:', str(text_res).encode('utf-8').decode('unicode_escape'), time.ctime())
                    print('save       :', str(text_save).encode('utf-8').decode('unicode_escape'), time.ctime())

                    if text_res.count('user_mobile'):
                        # 抢座成功就返回
                        preserve_success = True
                        print("🐮恭喜！明日预约成功！记得早起🍺")
                        try:
                            my_email.goLib_email_info('success', json.loads(text_res))
                        except Exception as e:
                            print(e)
                            print('获取每日诗词失败或发送邮件失败。。。')
                        finally:
                            # 成功直接返回True，同时恢复queue_header
                            if queue_header[-1][0] == 'Cookie':
                                queue_header.pop()
                            break
                    else:
                        # 两次抢座间隔1s
                        time.sleep(1)

            except Exception as e:
                print(e)
                time.sleep(0.3)

            finally:
                # 如果抢座已经开始了超过12s了，没必要继续下去了
                if preserve_success:
                    break
                if time.time() - open_time >= 12:
                    # finally，保证程序退出的时候，恢复queue_header
                    if queue_header[-1][0] == 'Cookie':
                        queue_header.pop()
                    break

    # 恢复queue_header
    if queue_header[-1][0] == 'Cookie':
        queue_header.pop()
    # 抢座失败的通知
    if not preserve_success:
        print(time_update().split(' ')[0] + "的抢座结束！")
        my_email.goLib_email_info('fail')


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
    # session 对象 =》 保活
    session = requests.session()
    print('🌠我去图书馆程序，启动！🌠 ', time.ctime())
    # 先进行一次session初始化设置，
    keep_session_newest(session=session, usr_list=usr_list)

    # 每3~5分钟刷新cookie, 保活session
    schedule.every(5).minutes.do(run_thread, param_dict={
        'func': keep_session_newest,
        'session': session,
        'usr_list': usr_list
    })
    # 每天21：59准时退座
    schedule.every().day.at("21:59:30").do(run_thread, param_dict={
        'func': withdraw_seat,
        'session': session,
        # 暂时---只给自己自动退座
        'usr': usr_list[0]
    })
    # 线程进行抢座！
    schedule.every().day.at("20:59:50").do(run_thread, param_dict={
        'func': preserve_tomorrow,
        'session': session,
        # 暂时---只给自己自动抢座
        'usr': usr_list[0]
    })

    while True:
        schedule.run_pending()
        time.sleep(1)
