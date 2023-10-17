"""
电子阅览室:             490
多功能阅览室:           491
二楼北社会科学阅览室: 122223
二楼南报刊:          122216
三楼南自然科学阅览室: 122202
三楼北语言文学:      122265
三楼北经济管理:      122272
四楼北自然科学阅览室: 122188
"""

# 填入选择的阅览室的id, 字符串形式
the_lib_chosen = [491]
# the_lib_chosen = [122202]  # 测试，三楼南的座位！
# 填入要选择的座位号， 字符串形式（数字两边加上'）

# the_seat_chosen = ['11,17', '8,10', '8,17']  # 多功能阅览室的座位！
the_seat_chosen = ['17,6', '8,10', '8,17']  # 多功能阅览室的座位！
# the_seat_chosen = ['53,5', '52,22']  # 测试，三楼南的座位！


# 请求头
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090621) XWEB/8391 Flue',
    'Content-Length': '1172',
    'Content-Type': 'application/json',
    'App-Version': '2.0.14',
    'Referer': 'https://web.traceint.com/',
    'Origin': 'https://web.traceint.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Connection': 'keep-alive',
    'Host': 'wechat.v2.traceint.com'
}
# url
url = 'http://wechat.v2.traceint.com/index.php/graphql/'

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

