import http.cookies
import json
import random
import time
import requests
import schedule
from lib_configs import *
import my_email


class User:
    def __init__(self, user: dict):
        self.name = user['name']
        self.email = user['email']
        self.tel = user['tel']
        self.cookie = user['cookie']
        self.pre_reserve_time = user['pre_reserve_time']
        self.close_lib_time = user['close_lib_time']
        self.lib_id = user['lib_id']
        self.seats = user['seats']
        self.session = requests.session()
        self.session.headers.update(pre_header)

        cookie = http.cookies.SimpleCookie()
        cookie.load(user['cookie'])
        for key, morsel in cookie.items():
            self.session.cookies.set(key, morsel)

    @staticmethod
    def keep_session(user_list):
        for user in user_list:
            if user.session.cookies.keys().count("Authorization") > 1:
                user.session.cookies.set("Authorization", domain="", value=None)
            res = user.session.post("http://wechat.v2.traceint.com/index.php/graphql/", json={
                "query": 'query getUserCancleConfig { userAuth { user { holdValidate: getSchConfig(fields: '
                         '"hold_validate", extra: true) } } }',
                "variables": {},
                "operationName": "getUserCancleConfig"
            })

            result = res.json()
            try:
                result = res.json()
            except json.decoder.JSONDecodeError as err:
                print("Error: %s" % err)
            if result.get("errors") and result.get("errors")[0].get("code") != 0:
                print("result: ", result)
                print("😥Session expired!😥")
                my_email.goLib_email_info('SessionError', )
            else:
                print(f"✅{user.name}Session OK✅,", time.ctime())

    @staticmethod
    def get_token_and_exp_date_str(user):
        # 通过这个请求对应的响应体来获取取消预约的令牌哦 以及最晚签到时间的时间戳
        json_data = user.session.post(url=url, json=params_index, verify=False).json()
        if json_data['data']['userAuth']['reserve']['reserve'] is None:
            return
        # 如果已经预定好了座位，获取对应的最晚签到时间 以及 退课令牌
        # 如果已经签到过，晚上自动退座，只需要获得退课令牌
        token = json_data['data']['userAuth']['reserve']['getSToken']
        exp_date = json_data['data']['userAuth']['reserve']['reserve']['exp_date']
        return exp_date, token

    @staticmethod
    def withdraw_seat(user):
        try:
            exp_date, token = user.get_token_and_exp_date_str(user)
            reserve_cancel["variables"]["sToken"] = token
            res = user.session.post(url=url, json=reserve_cancel, verify=False).json()
            if res["data"]["userAuth"]["reserve"]["reserveCancle"]["timerange"] > 0:
                print(user.name, '退座成功！', time.ctime())
            else:
                print('已获取sToken但是退座失败！')
        except:
            print('🚨退座失败！请先选择一个座位！', time.ctime())

    @staticmethod
    def cookie_dict_to_str_with_equal(cookie_dict: dict):
        return str(cookie_dict).strip('{}').replace("'", "").replace('"', "") \
            .replace(': ', '=').replace(":", '=').replace(',', ';')

    def set_cookie(self, cookie):
        self.cookie = cookie

    def __str__(self):
        return "name:{}, email:{}, tel:{}, ".format(self.name, self.email, self.tel) + '\r\n' \
             + "pre_reserve_time:{}, lib_id:{}, seats:{}".format(self.pre_reserve_time, self.lib_id, self.seats)
    __repr__ = __str__
    '''
    __repr__ = __str__ 使用时可保证在控制台>>> print() 时 任然输出
    学号:111--姓名:Bob--年龄18
    '''


if __name__ == '__main__':
    User_list = []
    requests.packages.urllib3.disable_warnings()
    with open('init_conf.json', 'r', encoding='utf-8') as fp:
        usr_list = json.loads(fp.read())['users']
    usr_list = list(filter(lambda x: x['cookie'] != "", usr_list))
    for usr in usr_list:
        User_list.append(User(usr))
    User.keep_session(User_list)
    # for User in User_list:
    #     print(User.session.cookies)
    schedule.every(4 * 60 + random.randint(-60, 60)).seconds.do(User.keep_session, User_list)

    while True:
        schedule.run_pending()
        time.sleep(1)

