import json
from ws4py.client.threadedclient import WebSocketClient
import websocket
import ssl
import base64
import os
import time
import asyncio


queue_header = [
    ('Host', 'wechat.v2.traceint.com'),
    ('Connection', 'Upgrade'),
    ('Upgrade', 'websocket'),
    ('Pragma', 'no-cache'),
    ('Cache-Control', 'no-cache'),
    ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090719) XWEB/8391 Flue'),
    ('Origin', 'https://web.traceint.com'),
    ('Accept-Encoding', 'gzip, deflate, br'),
    ('Accept-Language', 'zh-CN,zh'),
    ('Sec-WebSocket-Extensions', 'permessage-deflate; client_max_window_bits'),
    # ('Sec-WebSocket-Key', 'J5PSBxALx6TJAVyRXIhl0g=='), # 这个东西是socket通信自带的，不需要自己加
    ('Sec-WebSocket-Version', '13')
    # (cookie)
]


def socket_key_random():
    # 生成16字节的随机值
    random_bytes = os.urandom(16)
    # 使用base64编码
    return base64.b64encode(random_bytes).decode('utf-8')
    # print("Sec-WebSocket-Key:", sec_websocket_key)


class CG_Client(WebSocketClient):

    open_time = None
    queue_start_time = None
    queue_end_time = None
    cnt_sent = 0
    cnt_revc = 0
    name = None
    # usr_info = {}

    def opened(self):
        while time.time() < self.queue_start_time:
            pass
        self.send('{"ns":"prereserve/queue","msg":""}')
        self.cnt_sent += 1
        print(self.cnt_sent, self.name, '>>> msg', time.time())
        # while True:
        #     # 到达开始排队的时间以及持续排队的时间
        #     # 在open_time的前后0.n s内持续发送排队消息。
        #     while self.queue_start_time <= time.time() <= self.queue_end_time:
        #         # 连发
        #         self.send('{"ns":"prereserve/queue","msg":""}')
        #         self.cnt_sent += 1
        #         print(self.cnt_sent, self.name, '>>> msg1', time.time())
        #         time.sleep(0.01)
        #     else:
        #         # 持续时间过了之后，每次只发送一次消息
        #         if time.time() >= self.open_time:
        #             self.send('{"ns":"prereserve/queue","msg":""}')
        #             self.cnt_sent += 1
        #             print(self.cnt_sent, self.name, '>>> msg2', time.time())
        #             break

    def closed(self, code, reason=None):
        # print("socket closed down:", code, reason)
        pass

    def received_message(self, resp):
        self.cnt_sent -= 1
        self.cnt_revc += 1
        resp_msg = str(resp)
        print(self.cnt_revc, self.name, '<<<', resp_msg, time.time())
        if resp_msg.find('u6392') != -1:  # 排队成功返回的第一个字符
            print('time consumption in queue:', time.time() - self.open_time)
            print('queue over')
            self.close()
        # elif resp_msg.find('u6210') != -1:  # 已经抢座成功的返回
        #     print("rsp msg:{}".format(json.loads(resp_msg)["msg"]))
        #     self.close()
        #     time.sleep(1)
        elif self.cnt_sent <= 0:
            self.opened()


if __name__ == '__main__':
    ws = None

    try:
        ws = CG_Client(
            url="wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
            headers=queue_header
            # ssl_options={'ssl': ssl_context}
            # ssl_options={}
        )
        now = time.time()
        ws.open_time = now + 1
        ws.queue_start_time = now
        ws.queue_end_time = now + 0.5
        ws.name = 'sss'
        # ws.queue_end_time = now + 0.3
        print(ws.open_time)

        cookie = 'SERVERID=d3936289adfff6c3874a2579058ac651|1698669930|1698669730; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjEwODY5ODU4LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNjk4NjcxNzY1fQ.APmdWz6QjKsbPOJGb9Qi1eFAeQ0hFNk1w3i2fL0J1Majd3BECqIw7NR4qsHjVej-hYEtN-UDF-3uQrhr9PKtHBUkMYXKKLsFxrPEhxkcQ9JcERmRv7gOPTavp2vgB6RvEBDtKmU2bHWJ6s4TE2L9Z2dqcl4xSkowuxQn5RQ0PbKPPMjFcJxaDJGNQuGD7TWfKxEat2mO3oUytNmswpzaQDitij5WdUL0GSUXs-aTALl8CZTslMaSs54qxR8AFma7gXR6BE0A7m9LrHtNq8jGsab7mdtfzWc2MBqj5xtXr3Bh370AVhIeGzY0L6cRkbw1VgTC71qBBe958wPhWiS-5w; SERVERID=e3fa93b0fb9e2e6d4f53273540d4e924|1698664566|1698664565'
        queue_header.append(('Cookie', cookie))
        start = time.time()
        ws.connect()
        ws.run_forever()

        end = time.time()
        print(end - start)
    except Exception as e:
        print('??')
        print(e)


    # # 第二种方法
    # queue_header = {
    #     'Host': 'wechat.v2.traceint.com',
    #     'Connection': 'Upgrade',
    #     'Pragma': 'no-cache',
    #     'Cache-Control': 'no-cache',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090719) XWEB/8391 Flue',
    #     'Upgrade': 'websocket',
    #     'Origin': 'https://web.traceint.com',
    #     'Sec-WebSocket-Version': '13',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'zh-CN,zh',
    #     # 'Sec-WebSocket-Key': 'h/hkRDGbwZ1VCVfpL54B8w==',
    #     'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
    #     'Cookie': 'Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjMyNjcxMzA3LCJzY2hJZCI6MTI1LCJleHBpcmVBdCI6MTY5NzQ3MTU0MH0.YxF4qJF0xzQdpa6OUcaEEJHyWK9hlT5nh66QGFjpqUFFuXJ03YMToFdfy_-GSyUez45ggPq1QU-eho54gnjTrEzI67Ra_2GNxkq1SPaXIMqIiYXZQ-s41Znuq0KFVd2HEYIN6cjfp1mQcS5_BjKUCZIKcEO0UTywJ9WYqfCI7Q_Kti5p7Gug9NFEzVqJfhqC2ey8CHQYajyd-OIHvYhS61RO5mUZWgESPTPE-L6P2d18HE--lUUPJiJCYxqHPifzUIhpQAytak3RplgEWhyW5_HPa_goD0WgGUS8FyjVTd_YU6yASVyFzElRitRiawilU_eUKV5AfubC9Zqj8rpuBQ; SERVERID=82967fec9605fac9a28c437e2a3ef1a4|1697466072|1697462331; SERVERID=d3936289adfff6c3874a2579058ac651|1696832980|1696832980'
    # }
    # start = time.time()
    # ws = websocket.create_connection('wss://wechat.v2.traceint.com/ws?ns=prereserve/queue',
    #                                  header=queue_header,
    #                                  sslopt={"cert_reqs": ssl.CERT_NONE})
    # if ws.connected:
    #     print('test pass queue connect')
    #     while True:
    #         ws.send('{"ns":"prereserve/queue","msg":""}')
    #         a = ws.recv()
    #         print(a)
    #         if a.find('u6392') != -1:  # 排队成功返回的第一个字符
    #             break
    #         if a.find('u6210') != -1:  # 已经抢座成功的返回
    #             print("rsp msg:{}".format(json.loads(str(a))["msg"]))
    #             time.sleep(5)
    #             break
    #         print("排队中，rsp:{}".format(a))
    #     # 关闭连接
    #     ws.close()
    # end = time.time()
    # print('time in queue:', end - start)
    # time.sleep(0.01)
    # print("排队结束。。。")
    # print("================================")
    # except KeyboardInterrupt:
    #     ws.close()

# if __name__ == '__main__':
#     ws = CG_Client(
#         url="ws://localhost:8765"
#         # headers=queue_header
#         # ssl_options={}
#     )
#     ws.open_time = time.time() + 0.5
#     ws.queue_start_time = time.time()
#     ws.queue_end_time = ws.open_time + 0.5
#     ws.connect()
#     ws.run_forever()

