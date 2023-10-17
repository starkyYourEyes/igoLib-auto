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
    "query": "mutation save($key: String!, $libid: Int!, $captchaCode: String, $captcha: String) {\n userAuth {\n prereserve {\n save(key: $key, libId: $libid, captcha: $captcha, captchaCode: $captchaCode)\n }\n }\n}",
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
    "query": "query libLayout($libId: Int!) {\n userAuth {\n prereserve {\n libLayout(libId: $libId) {\n max_x\n max_y\n seats_booking\n seats_total\n seats_used\n seats {\n key\n name\n seat_status\n status\n type\n x\n y\n }\n }\n }\n }\n}",
    "variables": {
        "libId": lib_id
    }
}
# prereserve
params_confirm_seat_info = {"operationName": "prereserve",
                            "query": "query prereserve {\n userAuth {\n prereserve {\n prereserve {\n day\n lib_id\n "
                                     "seat_key\n seat_name\n is_used\n user_mobile\n id\n lib_name\n }\n }\n }\n}"}

url = 'https://wechat.v2.traceint.com/index.php/graphql/'

pre_header = {
    'Host': 'wechat.v2.traceint.com',
    'Connection': 'keep-alive',
    'Content-Length': '309',
    'App-Version': '2.0.14',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090719) XWEB/8391 Flue',
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


def queue_pass(ws):
    # 连接socket进行排队的几种方法
    # 第一种方法
    # ws = websocket.WebSocket()
    # ws.connect('wss://wechat.v2.traceint.com/ws?ns=prereserve/queue', header=queue_header)  # 这里的XXXX和Host内容是一致的

    # 第二种方法
    # ws = websocket.create_connection('wss://wechat.v2.traceint.com/ws?ns=prereserve/queue',
    #                                  header=queue_header,
    #                                  sslopt={"cert_reqs": ssl.CERT_NONE})
    # if ws.connected:
    #     print('test pass queue connect')
    #     while True:
    #         ws.send('{"ns":"prereserve/queue","msg":""}')
    #         a = ws.recv()
    #         print(a)
    #         if a.find('u6392') != -1:  # 排队成功返回的第一个字符
    #             break
    #         if a.find('u6210') != -1:  # 已经抢座成功的返回
    #             print("rsp msg:{}".format(json.loads(str(a))["msg"]))
    #             time.sleep(5)
    #             break
    #         print("排队中，rsp:{}".format(a))
    #     # 关闭连接
    #     ws.close()
    # time.sleep(0.01)
    # print("排队结束。。。")
    # print("================================")

    """第三种方法"""
    # ws = CG_Client(
    #     url="wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
    #     headers=queue_header
    # )
    # 在抢座开始之前就已经建立好了这个socket，节省时间
    ws.connect()
    ws.run_forever()


async def queue_pass_websockets(open_time):
    """
    經過實驗，知道了，即使沒到明日預約開始的時間，仍然可以連接服務器，所以可以省下來連接服務器的時間
    由此建立第四種方法
    """
    # 创建一个 SSL 上下文并指定协议版本
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect("wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
                                  extra_headers=queue_header_for_websockets,
                                  ssl=ssl_context) as websocket:
        # 在搶座開始前0.5s就對服務器開始狂轟濫炸😝
        start_preserve = open_time - 0.5
        while True:  # 外循环控制时间
            if time.time() >= start_preserve:
                while True:  # 内循环控制socket通信，直到收到排队成功的消息
                    try:
                        await websocket.send('{"ns":"prereserve/queue","msg":""}')
                        ans = await websocket.recv()
                        if ans.find('u6392') != -1 or ans.find('u6210') != -1:  # 成功排队，2分钟内。。。。
                            # \u6392排好队返回的第一个字，   \u6210已经抢完座返回的第一个字
                            print(json.loads(ans)["msg"])
                            break  # 跳出内层循环
                    except Exception as e:
                        time.sleep(0.3)
                        print(e)
                    # print("Queuing...")
                    print(json.loads(ans)["msg"])
                break  # 跳出外层循环


def time_update():
    """
    每天搶座函數開始執行的時候，更新當前時間（搶座開放時間）
    :return:
    """
    # struct_openTime = "****-**-** 21:00:00"
    now = time.gmtime()
    return now.tm_year.__str__() + '-' \
           + now.tm_mon.__str__() + '-' \
           + now.tm_mday.__str__() + ' ' \
           + '21:00:00'


# 开始时间
def preserve_tomorrow(session, usr: dict):
    # 更新cookie
    cookie = usr['cookie']
    # websocket的请求头的形式 => dict
    queue_header_for_websockets['Cookie'] = cookie
    # ws4py的请求头的形式 => tuples list
    # queue_header.append(('Cookie', cookie))
    # http请求的请求头
    pre_header['Cookie'] = cookie

    # 更新为当日抢座时间,open_time -> 时间戳
    open_time = time.mktime(time.strptime(time_update(), "%Y-%m-%d %H:%M:%S"))
    # 时间戳转换成localtime,
    # 形如：time.struct_time(tm_year=2023, tm_mon=9, tm_mday=25, tm_hour=12, tm_min=22, tm_sec=18,tm_wday=0, tm_yday=268, tm_isdst=0)
    # 转换成新的时间格式(2016-05-05 20:28:54)
    print('🙏明日预约初始化完成！')
    print('当前时间：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), end=', ')
    print('还有%f秒开始' % (open_time - time.time()))
    # # 先建立一个socket
    # ws = CG_Client(
    #     url="wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
    #     headers=queue_header
    # )
    while True:
        if time.time() >= open_time:
            # print(time.time(), "⏰时间到，准备开始抢座!")
            # start_time = time.time()
            """ws4py"""
            # # 排队！直接省去函数调用！
            # # queue_pass(ws)
            # ws.connect()
            # ws.run_forever()
            """websockets"""
            asyncio.run(queue_pass_websockets(open_time))
            # print(time.time(), '🚥queue ==> ok!')
            try:
                for seat in the_seat_chosen:
                    # 重要！如果不是放在常用座位，需要先请求对应的阅览室的所有座位，libLayout！！
                    session.post(
                        url=url,
                        headers=pre_header,
                        json=data_lib_chosen,  # libLayout
                        verify=False
                    )
                    # 抢座的post请求，core code
                    params_confirm_seat['variables']['key'] = seat + '.'
                    # print(params_confirm_seat)
                    text_save = session.post(
                        url=url,
                        headers=pre_header,
                        json=params_confirm_seat,  # save
                        verify=False
                    ).text
                    # print('⏰time when start queue:            ', start_time)
                    # print('⏰time consumption in queue:        ', queue_time - start_time)
                    print('🚒save  ==> ok!')
                    # print('⏰time consumption to preserve seat:', time.time() - queue_time)
                    # print(res.text)
                    text_res = session.post(
                        url=url,
                        headers=pre_header,
                        json=params_confirm_seat_info,  # prereserve
                        verify=False
                    ).text
                    print(time.ctime(), 'pre reserve:', str(text_res).encode('utf-8').decode('unicode_escape'))
                    print(time.ctime(), 'save       :', str(text_save).encode('utf-8').decode('unicode_escape'))

                    # if str(text_save).count("true") and text_res.count('user_mobile'):
                    if text_res.count('user_mobile'):
                        # 抢座成功就返回
                        print("😍恭喜你！明日预约成功！记得早起")
                        # queue_header.pop()
                        try:
                            my_email.goLib_email_info('success', json.loads(text_res))
                        except Exception as e:
                            print(e)
                            print('获取每日诗词失败。。。')
                        return True
                    else:
                        # ws = CG_Client(
                        #     url="wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
                        #     headers=queue_header
                        # )
                        # 连续两次抢座之间间隔至少1s。。。。
                        time.sleep(1)
            except Exception as e:
                time.sleep(0.3)
                print(e)
            break
    # 抢座失败的通知
    # queue_header.pop()
    my_email.goLib_email_info('fail')
    return False


def keep_pre_reserve(session, usr):
    # 重复3次！
    for i in range(0, 1):
        if preserve_tomorrow(session=session, usr=usr):
            break
    print(time_update().split(' ')[0] + "的抢座结束！")


# @catch_exceptions(cancel_on_failure=False)
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
    schedule.every(4 * 60 + random.randint(-60, 60)).seconds.do(run_thread, param_dict={
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
    schedule.every().day.at("20:59:55").do(run_thread, param_dict={
        'func': preserve_tomorrow,
        'session': session,
        # 暂时---只给自己自动抢座
        'usr': usr_list[0]
    })
    # schedule.every().day.at("20:59:00").do(run_thread, {
    #     'func': preserve_tomorrow,
    #     'session': session,
    #     'file_name': 'cookie_me.txt'
    # })

    while True:
        schedule.run_pending()
        time.sleep(1)


