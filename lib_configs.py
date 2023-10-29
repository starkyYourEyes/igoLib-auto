import time
def time_update(when='20:00:00'):
    """明日预约时间
    每天搶座函數開始執行的時候，更新當前時間（搶座開放時間）"""
    # struct_openTime = "****-**-** 21:00:00"
    now = time.gmtime()
    return now.tm_year.__str__() + '-' \
           + now.tm_mon.__str__() + '-' \
           + now.tm_mday.__str__() + ' ' \
           + when


# the_lib_chosen = [491]
# the_seat_chosen = ['17,6', '11,17', '17,18']  # demo, 17, 6 => 70
the_lib_chosen = [122202]  # 测试，三楼南的座位！
the_seat_chosen = ['53,5', '52,22']  # 测试，三楼南的座位！
# 填入要选择的座位号， 字符串形式（数字两边加上'）
# #                    49号     44号
# the_seat_chosen = ['11,17', '14,17', '8,17']  # 多功能阅览室的座位！
#                    70号    49号      38号



"""henan"""
# the_lib_chosen = [10086]  # want
# the_seat_chosen = ['24,15', '20,15', '14,16', '24,16', '22,15']  # seat want

# the_lib_chosen = [11082]  # demo
# the_seat_chosen = ['9,13', '10,7', '11,7', '11,13', '13,11']  # demo

# 请求头
headers = pre_header = {
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

url = 'https://wechat.v2.traceint.com/index.php/graphql/'

queue_header_for_websockets = {
    'Host': 'wechat.v2.traceint.com',
    'Connection': 'Upgrade',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090719) XWEB/8391 Flue',
    'Upgrade': 'websocket',
    'Origin': 'https://web.traceint.com',
    'Sec-WebSocket-Version': '13',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh',
    # 'Sec-WebSocket-Key': 'h/hkRDGbwZ1VCVfpL54B8w==',
    'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
    'Cookie': '***'
}

# prereserve
params_confirm_seat_info = {"operationName": "prereserve",
                            "query": "query prereserve {\n userAuth {\n prereserve {\n prereserve {\n day\n lib_id\n "
                                     "seat_key\n seat_name\n is_used\n user_mobile\n id\n lib_name\n }\n }\n }\n}"}

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

# basic configs
seat_key, lib_id = the_seat_chosen[0], the_lib_chosen[0]
# save
params_confirm_seat = {
    "operationName": "save",
    "query": "mutation save($key: String!, $libid: Int!, $captchaCode: String, $captcha: String) {\n userAuth {\n "
             "prereserve {\n save(key: $key, libId: $libid, captcha: $captcha, captchaCode: $captchaCode)\n }\n }\n}",
    "variables": {
        # 这里的"key"：如果不是常用座位，需要在最后面加一个 '.'
        "key": '***',
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

if __name__ == '__main__':
    print(time_update())
