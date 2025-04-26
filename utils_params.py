import time
import urllib.request
import urllib.parse
import http.cookiejar


def time_update(when='20:00:00'):
    """明日预约时间
    每天搶座函數開始執行的時候，更新當前時間（搶座開放時間）"""
    # struct_openTime = "****-**-** 21:00:00"
    now = time.gmtime()
    return now.tm_year.__str__() + '-' \
           + now.tm_mon.__str__() + '-' \
           + now.tm_mday.__str__() + ' ' \
           + when


def fetch_cookie_string():
    url = input("Please enter the URL: ")
    query = urllib.parse.urlparse(url).query
    codes = urllib.parse.parse_qs(query).get('code')
    if codes:
        codes = codes.pop()
    else:
        raise ValueError("Code not found in URL")
    # url = 'http://wechat.v2.traceint.com/index.php/graphql/?operationName=index&query=query%7BuserAuth%7BtongJi
    # %7Brank%7D%7D%7D&code=011Kkf1w3ryUo13m3L3w3JVWZD3Kkf19&state=1'
    cookiejar = http.cookiejar.MozillaCookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))
    response = opener.open(
        "http://wechat.v2.traceint.com/index.php/urlNew/auth.html?" + urllib.parse.urlencode({
            "r": "http://wechat.v2.traceint.com/index.php/graphql/web/index.html",
            "code": codes,
            "state": 1
        })
    )
    # print(response)
    cookie_items = []
    for cookie in cookiejar:
        cookie_items.append(f"{cookie.name}={cookie.value}")
    cookie_string = '; '.join(cookie_items)
    # print(cookie_string)
    return cookie_string


url = 'https://wechat.v2.traceint.com/index.php/graphql/'

headers = pre_header = {
    'Host': 'wechat.v2.traceint.com',
    'Connection': 'keep-alive',
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
    # 'Sec-WebSocket-Key': 'h/==',
    'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
    'Cookie': '***'
}

prereserve_operation = {"operationName": "prereserve",
                        "query": "query prereserve {\n userAuth {\n prereserve {\n prereserve {\n day\n lib_id\n "
                                 "seat_key\n seat_name\n is_used\n user_mobile\n id\n lib_name\n }\n }\n }\n}"}

index_operation = {
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

# save. oops, be careful when change and use this param, 多线程！临界资源！
save_operation = {
    "operationName": "save",
    "query": "mutation save($key: String!, $libid: Int!, $captchaCode: String, $captcha: String) {\n userAuth {\n "
             "prereserve {\n save(key: $key, libId: $libid, captcha: $captcha, captchaCode: $captchaCode)\n }\n }\n}",
    "variables": {
        # 这里的"key"，需要在最后面加一个 '.'
        "key": '***' + '.',
        "libid": 10086,
        "captchaCode": "",
        "captcha": ""
    }
}
# libLayout oops, be careful when change and use this param, 多线程！临界资源！
libLayout_operation = { # 注意这个参数里面有一个 preresserve ——说明请求的是明日预约的座位状态。
    "operationName": "libLayout",
    "query": "query libLayout($libId: Int!) {\n userAuth {\n prereserve {\n libLayout(libId: $libId) {\n max_x\n "
             "max_y\n seats_booking\n seats_total\n seats_used\n seats {\n key\n name\n seat_status\n status\n type\n "
             "x\n y\n }\n }\n }\n }\n}",
    "variables": {
        "libId": 10086
    }
}

getUserCancleConfig_operation = {
    "query": 'query getUserCancleConfig { userAuth { user { holdValidate: getSchConfig(fields: "hold_validate", extra: true) } } }',
    "variables": {},
    "operationName": "getUserCancleConfig"
}
reserveCancel_operation = {
    "operationName": "reserveCancle",
    "query": "mutation reserveCancle($sToken: String!) {\n userAuth {\n reserve {\n reserveCancle(sToken: "
             "$sToken) {\n timerange\n img\n hours\n mins\n per\n }\n }\n }\n}",
    "variables": {
        "sToken": "***********"
    }
}

if __name__ == '__main__':
    # print(time_update())
    print(fetch_cookie_string())
