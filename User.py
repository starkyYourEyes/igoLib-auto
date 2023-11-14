import copy
import http.cookies
import json
import random
import time
import requests
from utils_params import *
import my_email


class User:
    def __init__(self, user: dict):
        if not isinstance(user, dict):
            raise TypeError("argument 'user' is not a dict, __init__ error!")
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
        user_cookies: list[dict] = []
        for user in user_list:
            time.sleep(2 * random.random())
            if user.session.cookies.keys().count("Authorization") > 1:
                user.session.cookies.set("Authorization", domain="", value=None)
            res = user.session.post(
                url="http://wechat.v2.traceint.com/index.php/graphql/",
                json=getUserCancleConfig_operation
            )
            user_cookies.append({
                "name": user.name,
                "cookie": User.cookie_dict_to_str_with_equal(
                    requests.utils.dict_from_cookiejar(user.session.cookies))
            })
            result = res.json()
            try:
                result = res.json()
            except json.decoder.JSONDecodeError as err:
                print("Error: %s" % err)
            if result.get("errors") and result.get("errors")[0].get("code") != 0:
                print("result: ", result)
                print(f"{user.name} Session expired!😥")
                my_email.goLib_email_info('SessionError')
            else:
                print(f"{user.name} Session OK✅,", time.ctime())

        try:
            with open('init_conf.json', 'r+', encoding='utf-8') as fp:
                users = json.loads(fp.read())  # read将文件指针移动到了最后
                """fp.seek(0)把文件指针的位置调回首行首字节，否则调用了truncate(0)，但是文件指针位置没变，
                写入的内容会继续写在之前的文件指针的位置，而前面的被删除的内容，会被\0代替，显示为NUL或0000"""
                fp.seek(0)
                fp.truncate(0)
                fp.flush()
                for uc in user_cookies:
                    for usr in users['users']:
                        if uc['name'] == usr['name'] and usr['cookie'] is not None and usr['cookie'] != "":
                            usr['cookie'] = uc['cookie']
                            break
                json.dump(users, fp, ensure_ascii=False, indent=2)
        except Exception as e:
            print(e)
            print('更新cookie文件出错')
            fp.write(json.dumps(users, indent=2))
            # json.dump(users, fp, ensure_ascii=False, indent=2)

    @staticmethod
    def get_token(user):
        # 通过这个请求对应的响应体来获取取消预约的令牌哦 以及最晚签到时间的时间戳
        json_data = user.session.post(url=url, json=index_operation, verify=False).json()
        if json_data['data']['userAuth']['reserve']['reserve'] is None:
            return
        # 如果已经预定好了座位，获取对应的最晚签到时间 以及 退课令牌
        # 如果已经签到过，晚上自动退座，只需要获得退课令牌
        token = json_data['data']['userAuth']['reserve']['getSToken']
        # exp_date = json_data['data']['userAuth']['reserve']['reserve']['exp_date']
        return token

    @staticmethod
    def withdraw_seat(user):
        res = None
        try:
            token = user.get_token(user)
            my_reserveCancel_operation = copy.deepcopy(reserveCancel_operation)
            my_reserveCancel_operation["variables"]["sToken"] = token
            res = user.session.post(url=url, json=my_reserveCancel_operation, verify=False).json()
            if res["data"]["userAuth"]["reserve"]["reserveCancle"]["timerange"] > 0:
                print(user.name, '退座成功！', time.ctime())
            else:
                print('已获取sToken但是退座失败！')
        except Exception as e:
            print(e)
            print(res)
            print(user.name, '退座失败！请先选择一个座位！', time.ctime())

    @staticmethod
    def cookie_dict_to_str_with_equal(cookie_dict: dict) -> str:
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
