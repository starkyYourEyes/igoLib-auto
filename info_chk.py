import http.cookies
import requests
import json
import time
import random
from threading import Thread
import my_email
import warnings

from utils_params import *
import User

cookie = ""
lib_id = 12345

def get_index():
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
    session = requests.session()
    index_data = session.post(url=url, json=index_operation, headers=headers, verify=False).json()
    print(index_data)


def libs_info():
    params = {
        "operationName": "index",
        "query": "query index {\n userAuth {\n user {\n prereserveAuto: getSchConfig(extra: true, fields: \"prereserve.auto\")\n }\n currentUser {\n sch {\n isShowCommon\n }\n }\n prereserve {\n libs {\n is_open\n lib_floor\n lib_group_id\n lib_id\n lib_name\n num\n seats_total\n }\n }\n oftenseat {\n prereserveList {\n id\n info\n lib_id\n seat_key\n status\n }\n }\n }\n}"
    }
    session = requests.session()
    lib_info_data = session.post(url=url, json=params, headers=headers, verify=False).json()
    print(lib_info_data)


def lib_layout():
    params = {
        "operationName": "libLayout",
        "query": "query libLayout($libId: Int!) {\n userAuth {\n prereserve {\n libLayout(libId: $libId) {\n max_x\n max_y\n seats_booking\n seats_total\n seats_used\n seats {\n key\n name\n seat_status\n status\n type\n x\n y\n }\n }\n }\n }\n}",
        "variables": {
            "libId": lib_id
        }
    }
    session = requests.session()
    lib_info_data = session.post(url=url, json=params, headers=headers, verify=False).json()
    print(lib_info_data)


if __name__ == '__main__':
    headers['Cookie'] = cookie
    get_index()
    libs_info()
    lib_layout()
