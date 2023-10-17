import http.cookies
import requests
import json
import time
import random
from threading import Thread
import my_email
import warnings


# 持久化存储cookie，同时文件中的cookie可以共享给其他程序
def save_cookies(cookie_str, file_name='cookie_me.txt'):
    warnings.warn('This method has been abandoned, files like "cookie.txt" no longer exists', DeprecationWarning)
    with open(file_name, 'w', encoding='utf-8') as fp:
        fp.write(cookie_str)


# 从文件中读取最新的cookie
def get_newest_cookie_by_txt(file_name='cookie_me.txt'):
    warnings.warn('This method has been abandoned, files like "cookie.txt" no longer exists', DeprecationWarning)
    with open(file_name, 'r', encoding='utf-8') as fp:
        read_cookie = fp.read()
    return read_cookie.strip('\r\n')


# def keep_session_newest(session, file_name):
def keep_session_newest(session, usr_list):

    for usr in usr_list:
        if usr['name'] != "" and usr["cookie"] != "":
            cookie = http.cookies.SimpleCookie()
            cookie.load(usr['cookie'])
            for key, morsel in cookie.items():
                session.cookies.set(key, morsel)
            # print(session.cookies)
            if session.cookies.keys().count("Authorization") > 1:
                session.cookies.set("Authorization", domain="", value=None)
            res = session.post("http://wechat.v2.traceint.com/index.php/graphql/", json={
                "query": 'query getUserCancleConfig { userAuth { user { holdValidate: getSchConfig(fields: "hold_validate", extra: true) } } }',
                "variables": {},
                "operationName": "getUserCancleConfig"
            })
            # print(res.request.headers['Cookie'])
            # 持久化存储cookie
            # save_cookies(res.request.headers['Cookie'], file_name)
            # 修改cookie
            usr['cookie'] = res.request.headers['Cookie']
            # session.headers.clear(), session.headers.update(res.request.headers['Cookie'])
            try:
                result = res.json()
            except json.decoder.JSONDecodeError as err:
                print("Error: %s" % err)
            if result.get("errors") and result.get("errors")[0].get("code") != 0:
                print("result: ", result)
                # 看是哪一个出错了
                print("😥Session expired!😥", usr['email'])
                my_email.goLib_email_info('SessionError')
            else:
                print(f"✅Session OK.✅: {usr['email']}", time.ctime())
                # if file_name.count('me'):
                #     print("✅Z's Session OK.✅ ", time.ctime())
                # else:
                #     print("✔T's Session OK.✔")


if __name__ == '__main__':
    keep_session_newest(" ")
