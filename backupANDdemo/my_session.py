import random
import time

import requests
import schedule

from keep_session import *

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

cnt = 0
pre = ''
# def keep_session_newest(session, usr):
def keep_session_newest(User):
    global cnt
    cnt += 1

    if User.session.cookies.keys().count("Authorization") > 1:
        User.session.cookies.set("Authorization", domain="", value=None)
    res = User.session.post("http://wechat.v2.traceint.com/index.php/graphql/", json={
        "query": 'query getUserCancleConfig { userAuth { user { holdValidate: getSchConfig(fields: "hold_validate", extra: true) } } }',
        "variables": {},
        "operationName": "getUserCancleConfig"
    })
    with open('save_cookie' + User.name + '.txt', 'a+', encoding='utf-8') as fp:
        fp.write(str(cnt) + '. ' + User.session.cookies.__str__() + '\n')
        fp.write(User.session.headers.__str__() + '\n')
        fp.write(res.request.headers.__str__() + '\n')
        fp.write(User.session.cookies.__str__() + '\n')

    result = res.json()
    try:
        result = res.json()
    except json.decoder.JSONDecodeError as err:
        print("Error: %s" % err)
    if result.get("errors") and result.get("errors")[0].get("code") != 0:
        print("result: ", result)
        print("😥Session expired!😥")
        my_email.goLib_email_info('SessionError')
    else:
        print(cnt, f"✅Session OK.✅: ", User.name, time.ctime())


if __name__ == '__main__':
    usr = {
        "name": "上山未归",
        "cookie":     'Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjMzNTA3NDIxLCJzY2hJZCI6MTI1LCJleHBpcmVBdCI6MTY5ODc1NDUyOH0.GVtFCUCG0OSlMp35VRl6UdnSEwVVCJRgcG4sXk9pd-TtDr9AfLf-wzwxmProYkqRHf0b0X0N3WdkNfCDAUIrboDngCtRgoef1guu5iVCMpwRkktf2jYedKp-YWVhfijEuhJzxVVjKGT5nxQ1OhcMs-i-YrZB2xdgrMR4uR05sfal32dpkqxqpra2GiOPGd833IwLrk_5qAqtD4yaZ5xeGP5dya2UlXVlklsTkDrKTh0k1A1JymM75FFBrRkEqEKQeakqFmBTVKtAacAE_246_rnSJnR4l7VfqTa5an_TgV0ZWl0fV-Q388jGIkV8K78tPmMNH3trDzBDUMi3ul5hGw; SERVERID=e3fa93b0fb9e2e6d4f53273540d4e924|1698747334|1698747328',
        "email": "1710680337@qq.com",
        "tel": 18237569900,
        "session": None,
        "pre_reserve_time": "19:59:57",
        "close_lib_time": "22:29:30",
        "lib_id": 10086,
        "seats": ["341", "333", "323", "342", "340"]
    }
    session = requests.session()
    session.headers.update(pre_header)

    keep_session_newest(session, usr)
    schedule.every(4 * 60 + random.randint(-60, 60)).seconds.do(keep_session_newest, **{
        'session': session,
        'usr': usr
    })
    while True:
        schedule.run_pending()
        time.sleep(1)
