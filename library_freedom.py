"""
功能：
1. 全部阅览室扫描，有空位就去抢（用处不大）
2. 只针对特定阅览室的座位
3. 针对特定阅览室的某一些座位
4. 只针对某一个阅览室的某一个座位

python 3.10
          _____                    _____                    _____                    _____                   _______                   _____
         /\    \                  /\    \                  /\    \                  /\    \                 /::\    \                 /\    \
        /::\    \                /::\____\                /::\    \                /::\    \               /::::\    \               /::\    \
        \:::\    \              /:::/    /               /::::\    \              /::::\    \             /::::::\    \             /::::\    \
         \:::\    \            /:::/    /               /::::::\    \            /::::::\    \           /::::::::\    \           /::::::\    \
          \:::\    \          /:::/    /               /:::/\:::\    \          /:::/\:::\    \         /:::/~~\:::\    \         /:::/\:::\    \
           \:::\    \        /:::/____/               /:::/__\:::\    \        /:::/__\:::\    \       /:::/    \:::\    \       /:::/__\:::\    \
           /::::\    \      /::::\    \              /::::\   \:::\    \      /::::\   \:::\    \     /:::/    / \:::\    \      \:::\   \:::\    \
  ____    /::::::\    \    /::::::\____\________    /::::::\   \:::\    \    /::::::\   \:::\    \   /:::/____/   \:::\____\   ___\:::\   \:::\    \
 /\   \  /:::/\:::\    \  /:::/\:::::::::::\    \  /:::/\:::\   \:::\    \  /:::/\:::\   \:::\____\ |:::|    |     |:::|    | /\   \:::\   \:::\    \
/::\   \/:::/  \:::\____\/:::/  |:::::::::::\____\/:::/  \:::\   \:::\____\/:::/  \:::\   \:::|    ||:::|____|     |:::|    |/::\   \:::\   \:::\____\
\:::\  /:::/    \::/    /\::/   |::|~~~|~~~~~     \::/    \:::\  /:::/    /\::/   |::::\  /:::|____| \:::\    \   /:::/    / \:::\   \:::\   \::/    /
 \:::\/:::/    / \/____/  \/____|::|   |           \/____/ \:::\/:::/    /  \/____|:::::\/:::/    /   \:::\    \ /:::/    /   \:::\   \:::\   \/____/
  \::::::/    /                 |::|   |                    \::::::/    /         |:::::::::/    /     \:::\    /:::/    /     \:::\   \:::\    \
   \::::/____/                  |::|   |                     \::::/    /          |::|\::::/    /       \:::\__/:::/    /       \:::\   \:::\____\
    \:::\    \                  |::|   |                     /:::/    /           |::| \::/____/         \::::::::/    /         \:::\  /:::/    /
     \:::\    \                 |::|   |                    /:::/    /            |::|  ~|                \::::::/    /           \:::\/:::/    /
      \:::\    \                |::|   |        bug        /:::/    /     退      |::|   |         散      \::::/    /             \::::::/    /
       \:::\____\               \::|   |                  /:::/    /              \::|   |                  \::/____/               \::::/    /
        \::/    /                \:|   |                  \::/    /                \:|   |                   ~~                      \::/    /
         \/____/                  \|___|                   \/____/                  \|___|                                            \/____/
"""

from utils_params import *
import urllib3
import requests
import json
import time
from preserve_seat_tomorrow import user_list

# 关闭警告
urllib3.disable_warnings()
# 我去图书馆url，对这个url进行各种post请求
url = 'https://wechat.v2.traceint.com/index.php/graphql/'

# 创建一个session对象
session = requests.Session()
session.headers.clear(), session.headers.update(headers)
seat_id = ''


# 1. 针对某一个阅览室的所有座位
def typical_libs_all_seats(user):
    # 更新cookie
    headers['Cookie'] = user_list[0]['cookie']
    count = 0
    lib_id = user.lib_id
    with open('./lib_info/lib%s.json' % lib_id, 'r', encoding='utf-8') as fp:
        content = fp.read()  # type(fp.read()) = string
        lib_info = json.loads(content)  # type(lib_info) = dict
    seat_ids = []
    for seat in lib_info['data']['userAuth']['reserve']['libs'][0]['lib_layout']['seats']:
        if seat['name']:
            seat_ids.append(seat['key'])
    # print(seat_ids)
    # print(len(lib_info['data']['userAuth']['reserve']['libs'][0]['lib_layout']['seats']))
    # print(len(seat_ids))
    for key in seat_ids:
        # 请求信息，修改为循环中取得的id
        reserve_body = {"operationName": "reserueSeat",
                        "query": "mutation reserueSeat($libId: Int!, $seatKey: String!, $captchaCode: String, "
                                 "$captcha: String!) {\n userAuth {\n reserve {\n reserueSeat(\n libId: $libId\n "
                                 "seatKey: $seatKey\n captchaCode: $captchaCode\n captcha: $captcha\n )\n }\n "
                                 "}\n}",
                        "variables": {"seatKey": key, "libId": lib_id, "captchaCode": "", "captcha": ""}}

        seats_data = session.post(url=url, headers=headers, json=reserve_body, verify=False).json()
        print(seats_data)
        try:
            if seats_data['data']['userAuth']['reserve']['reserueSeat']:
                print("抢座成功：")
                break
        except:
            print("抢座时出错")
            break
        count += 1
        print("我去图书馆抢座：%d次尝试" % count)
        time.sleep(1)


# 2. 针对特定阅览室的一些特定座位
def typical_lib_typical_seats():
    # 更新cookie
    headers['Cookie'] = user_list[0]['cookie']
    seat_keys, lib_ids = 'the_seat_chosen', 'the_lib_chosen'
    assert type(seat_keys) is list and type(lib_ids) is list
    for lib, seat in seat_keys, lib_ids:
        # 请求信息，修改为循环中取得的id
        reserve_body = {"operationName": "reserueSeat",
                        "query": "mutation reserueSeat($libId: Int!, $seatKey: String!, $captchaCode: String, "
                                 "$captcha: String!) {\n userAuth {\n reserve {\n reserueSeat(\n libId: $libId\n "
                                 "seatKey: $seatKey\n captchaCode: $captchaCode\n captcha: $captcha\n )\n }\n "
                                 "}\n}",
                        "variables": {"seatKey": seat, "libId": lib, "captchaCode": "", "captcha": ""}}

        seats_data = session.post(url=url, json=reserve_body, verify=False).json()
        print(seats_data)

        try:
            if seats_data['data']['userAuth']['reserve']['reserueSeat']:
                print("抢座成功：")
                return True
            else:
                return False
        except Exception as e:
            return False


# 3. 只针对某一个阅览室的某一个座位
def typical_one():
    # 更新cookie
    headers['Cookie'] = user_list[0]['cookie']
    # 获得对应的座位号以及阅览室id
    seat_key, lib_id = 'the_seat_chosen[0]', 'the_lib_chosen[0]'
    assert type(seat_key) is int and type(lib_id) is str
    # 请求信息，修改为循环中取得的id
    reserve_body = {"operationName": "reserueSeat",
                    "query": "mutation reserueSeat($libId: Int!, $seatKey: String!, $captchaCode: String, "
                             "$captcha: String!) {\n userAuth {\n reserve {\n reserueSeat(\n libId: $libId\n "
                             "seatKey: $seatKey\n captchaCode: $captchaCode\n captcha: $captcha\n )\n }\n "
                             "}\n}",
                    "variables": {"seatKey": seat_key, "libId": lib_id, "captchaCode": "", "captcha": ""}}

    seats_data = session.post(url=url, headers=headers, json=reserve_body, verify=False).json()
    print(seats_data)
    # 更新cookie？
    # write_and_update(s, item, json_data_file, myheaders)
    try:
        if seats_data['data']['userAuth']['reserve']['reserueSeat']:
            print("抢座成功：")
            return True
        else:
            return False
    except Exception as e:
        return False


# 4. 全部阅览室扫描，有空位就去抢（用处不大）
def all_libs_random():
    # 更新cookie
    headers['Cookie'] = user_list[0]['cookie']
    params = {"operationName": "list",
              "query": "query list {\n userAuth {\n reserve {\n libs(libType: -1) {\n lib_id\n lib_floor\n is_open\n "
                       "lib_name\n lib_type\n lib_group_id\n lib_comment\n lib_rt {\n seats_total\n seats_used\n "
                       "seats_booking\n seats_has\n reserve_ttl\n open_time\n open_time_str\n close_time\n "
                       "close_time_str\n advance_booking\n }\n }\n libGroups {\n id\n group_name\n }\n reserve {\n "
                       "isRecordUser\n }\n }\n record {\n libs {\n lib_id\n lib_floor\n is_open\n lib_name\n lib_type\n "
                       "lib_group_id\n lib_comment\n lib_color_name\n lib_rt {\n seats_total\n seats_used\n "
                       "seats_booking\n seats_has\n reserve_ttl\n open_time\n open_time_str\n close_time\n "
                       "close_time_str\n advance_booking\n }\n }\n }\n rule {\n signRule\n }\n }\n}"}
    json_data = session.post(url=url, json=params, verify=False).json()
    print("list：", json_data)
    '''
    反复抢座，有座就抢
    '''
    count = 0  # 记录抢座的尝试次数
    while True:
        lib_id = ''
        lib_name = ''
        seats_rest = 0
        try:
            # 查看某一个阅览室是否有剩余座位，如果有，取到阅览室的id
            for lib in json_data['data']['userAuth']['reserve']['libs']:
                if lib['is_open'] and int(lib['lib_rt']['seats_has']) != 0:
                    lib_id = lib['lib_id']
                    lib_name = lib['lib_name']
                    seats_rest = int(lib['lib_rt']['seats_has'])
                    break
            print('===========================================================')
            print("请求阅览室列表成功")
        except:
            print("请求阅览室列表失败", json_data)
            break
        # 请求错误，继续请求
        if lib_id == '':
            continue

        print('当前阅览室：%s，座位剩余: %s, 努力抢座中……' % (lib_name, seats_rest))
        # 注意请求参数中的libID修改为上述lib_id
        check_floor_body = {"operationName": "libLayout",
                            "query": "query libLayout($libId: Int, $libType: Int) {\n userAuth {\n reserve {\n libs("
                                     "libType: $libType, libId: $libId) {\n lib_id\n is_open\n lib_floor\n lib_name\n "
                                     "lib_type\n lib_layout {\n seats_total\n seats_booking\n seats_used\n max_x\n "
                                     "max_y\n seats {\n x\n y\n key\n type\n name\n seat_status\n status\n }\n }\n "
                                     "}\n }\n }\n}",
                            "variables": {"libId": lib_id}}
        seats_data = session.post(url=url, json=check_floor_body, verify=False).json()
        # json_data = seats_data.json()
        # update cookie
        # write_and_update(s, item, json_data_file, myheaders)
        seat_id = ''
        seat_name = ''
        try:
            print('获取座位信息成功')
            for seat in seats_data['data']['userAuth']['reserve']['libs'][0]['lib_layout']['seats']:
                if seat['seat_status'] == 1:
                    # print('seat_status的类型为', type(seat['seat_status']))
                    seat_id = seat['key']
                    seat_name = seat['name']
                    break
        except:
            print('请求位置信息失败', seats_data)
            break
        if seat_id == '':
            continue

        print('******************************')
        print('选择的阅览室id：%s\n选择的座位id：%s' % (lib_name, seat_name))
        print('******************************')
        # 请求信息，修改为循环中取得的id
        reserve_body = {"operationName": "reserueSeat",
                        "query": "mutation reserueSeat($libId: Int!, $seatKey: String!, $captchaCode: String, "
                                 "$captcha: String!) {\n userAuth {\n reserve {\n reserueSeat(\n libId: $libId\n "
                                 "seatKey: $seatKey\n captchaCode: $captchaCode\n captcha: $captcha\n )\n }\n "
                                 "}\n}",
                        "variables": {"seatKey": seat_id, "libId": '490', "captchaCode": "", "captcha": ""}}

        seats_data = session.post(url=url, json=reserve_body, verify=False).json()
        print(seats_data)
        # 更新cookie？
        # write_and_update(s, item, json_data_file, myheaders)
        try:
            if seats_data['data']['userAuth']['reserve']['reserueSeat']:
                print("抢座成功：")
                break
        except:
            print("抢座时出错")
            break
        count += 1
        print("我去图书馆抢座：%d次尝试" % count)
        time.sleep(1)


if __name__ == '__main__':
    # all_libs_random()
    typical_one()
