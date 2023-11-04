from datetime import datetime

from utils_params import *
import requests


index_param = {
    "operationName": "index",
    "query": "query index($pos: String!, $param: [hash]) {\n userAuth {\n oftenseat {\n list {\n id\n info\n lib_id\n seat_key\n status\n }\n }\n message {\n new(from: \"system\") {\n has\n from_user\n title\n num\n }\n indexMsg {\n message_id\n title\n content\n isread\n isused\n from_user\n create_time\n }\n }\n reserve {\n reserve {\n token\n status\n user_id\n user_nick\n sch_name\n lib_id\n lib_name\n lib_floor\n seat_key\n seat_name\n date\n exp_date\n exp_date_str\n validate_date\n hold_date\n diff\n diff_str\n mark_source\n isRecordUser\n isChooseSeat\n isRecord\n mistakeNum\n openTime\n threshold\n daynum\n mistakeNum\n closeTime\n timerange\n forbidQrValid\n renewTimeNext\n forbidRenewTime\n forbidWechatCancle\n }\n getSToken\n }\n currentUser {\n user_id\n user_nick\n user_mobile\n user_sex\n user_sch_id\n user_sch\n user_last_login\n user_avatar(size: MIDDLE)\n user_adate\n user_student_no\n user_student_name\n area_name\n user_deny {\n deny_deadline\n }\n sch {\n sch_id\n sch_name\n activityUrl\n isShowCommon\n isBusy\n }\n }\n }\n ad(pos: $pos, param: $param) {\n name\n pic\n url\n }\n}",
    "variables": {
        "pos": "App-首页"
    }
}
reserveCancel_operation = {
    "operationName": "reserveCancle",
    "query": "mutation reserveCancle($sToken: String!) {\n userAuth {\n reserve {\n reserveCancle(sToken: "
             "$sToken) {\n timerange\n img\n hours\n mins\n per\n }\n }\n }\n}",
    "variables": {
        "sToken": "***********"
    }
}


def get_token_and_exp_date_str(usr):
    # 通过这个请求对应的响应体来获取取消预约的令牌哦
    # 以及最晚签到时间的时间戳
    pre_header['Cookie'] = usr['cookie']
    json_data = requests.post(url=url, headers=pre_header, json=index_param, verify=False).json()
    # print('=============================headers.item()=======================================')
    # print(session.headers.items())
    # print('=============================cookie信息================================')
    # print(session.cookies)
    #
    # # 如果还没有选择座位，不可退座，也没有对应的最晚签到时间
    # print(json_data)
    try:
        if json_data['data']['userAuth']['reserve']['reserve'] is None:
            print('🚨请先选择一个座位！')
            return
    except Exception as e:
        print(e)
        print('出现错误，cookie失效 或者 还没有选座')
    # 如果已经预定好了座位，获取对应的最晚签到时间 以及 退课令牌
    # 如果已经签到过，晚上自动退座，只需要获得退课令牌
    token = json_data['data']['userAuth']['reserve']['getSToken']
    exp_date = json_data['data']['userAuth']['reserve']['reserve']['exp_date']
    return exp_date, token


def withdraw_seat(usr):
    # print('开始退座')
    # print('token = ', token)
    # print(res)
    try:
        pre_header['Cookie'] = usr['cookie']
        exp_date, token = get_token_and_exp_date_str(usr)
        reserveCancel_operation["variables"]["sToken"] = token
        headers['Cookie'] = usr['cookie']
        res = requests.post(url=url, headers=pre_header, json=reserveCancel_operation, verify=False).json()
        if res["data"]["userAuth"]["reserve"]["reserveCancle"]["timerange"] > 0:
            print(usr['name'], '退座成功！', time.ctime())
        else:
            print('已获取sToken但是退座失败！')
    except Exception as e:
        print(e)
        print('退座失败！请先选择一个座位！', time.ctime())


# 暂时没有用处的函数~~
# def keep_reserving(session, exp_date, token, usr):
#     reserveCancel_operation["variables"]["sToken"] = token
#
#     while True:
#         # 如果最后签到时间小于5分钟，则取消预约，并退出函数
#         if exp_date - datetime.now().timestamp() <= 5 * 59:
#
#             while True:
#                 # 更新令牌
#                 new_exp, token = get_token_and_exp_date_str(session, usr=usr)
#                 reserveCancel_operation['variables']['sToken'] = token
#                 headers['Cookie'] = usr['cookie']
#                 quit_seat = session.post(url=url, headers=headers, json=reserveCancel_operation, verify=False).json()
#                 try:
#                     if '成功' in quit_seat['errors'][0]['msg']:
#                         print('😸取消预约成功，一分钟后进行再次预约😸')
#                         break
#                 except:
#                     print('😿取消预约时出错，重新请求中。。。😿')
#
#             # print(json_data)
#             # 一分钟后重新进行预约
#             time.sleep(60.5)
#             # 一直进行抢座
#             count = 0
#             while not typical_one():
#                 count += 1
#                 print('出错了，正在进行第%d次抢座' % count)
#                 time.sleep(0.5)
#             # 抢到座位之后，更新exp_date，继续循环
#             exp_date, token = get_token_and_exp_date_str(session)
#         # 否则，休眠一分钟半
#         else:
#             print('😉稍等，五分之三坤分钟后再次尝试退座😉')
#             time.sleep(90)

#
# if __name__ == '__main__':
#     # 关闭警告
#     urllib3.disable_warnings()
#     s = requests.session()
#     # 添加头信息以及cookie
#     headers['Cookie'] = get_newest_cookie_by_txt('cookie_me.txt')
#     s.headers.clear()
#     s.headers.update(headers)
#
#     # get_seat(s)
#     exp_date, token = get_token_and_exp_date_str(s)
#
#     keep_reserving(s, exp_date, token)
#
#     # now = datetime.now().timestamp()
#     # print((now - 1694932104) / 60)
#

    # s = requests.session()
    # headers['Cookie'] = get_newest_cookie_by_txt()
    # print(get_token_and_exp_date_str(session=s, header=headers))
