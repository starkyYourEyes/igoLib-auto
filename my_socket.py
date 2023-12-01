from ws4py.client.threadedclient import WebSocketClient
import ssl
import time


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
]


class CG_Client(WebSocketClient):

    # open_time = None
    queue_start_time = None
    queue_end_time = None
    user_name = None
    sent, revc = 0, 0

    def opened(self):
        while True:  # 到达开始排队的时间以及持续排队的时间
            while self.queue_start_time <= time.time() <= self.queue_end_time:
                # 连发，在open_time的前后0.n s内持续发送排队消息。
                self.send('{"ns":"prereserve/queue","msg":""}')
                self.sent += 1
                print(self.sent, f'{self.user_name} >>> msg1', time.time())
                time.sleep(0.03)
            else:
                # 持续时间过了之后，每次只发送一次消息
                if time.time() > self.queue_end_time:
                    self.send('{"ns":"prereserve/queue","msg":""}')
                    self.sent += 1
                    print(self.sent, f'{self.user_name} >>> msg2', time.time())
                    break

    def closed(self, code, reason=None):
        print(f"{self.user_name}'s socket closed down:", code, reason)

    def received_message(self, resp):
        resp_msg = str(resp)
        self.revc += 1
        self.sent -= 1
        print(self.revc, f'{self.user_name} <<<', resp_msg, time.time())
        if resp_msg.find('u6392') != -1 or self.revc >= 666:  # 排队成功返回的第一个字符
            print('queue over')
            self.close()
        # elif resp_msg.find('u6210') != -1:  # 已经抢座成功的返回
        #     print("rsp msg:{}".format(json.loads(resp_msg)["msg"]))
        #     self.close()
        #     time.sleep(1)
        else:
            if self.sent < 1:
                self.send('{"ns":"prereserve/queue","msg":""}')
                print(f'{self.user_name} >>> msg2', time.time())


if __name__ == '__main__':
    ws = None
    cookie = 'Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjM0Mzc3NTkxLCJzY2hJZCI6MTI1LCJleHBpcmVBdCI6MTY5OTE5MzUxMX0.v-mTMsWbFrMQ1H7jv-zQmxD41mfqwy4sEfMt0FL6_LJfScrH9RwIdfwavyW5cOjkEOG_-oXooXzFvbLLiXYaVAibHHC7GjqAqoaP5hAkMDYcTiCPK5FMblDGuAOzWZN66a9gcdnL9wR0Vpe5MFZBGxf8kLM0Lqk-jgCdjgMRL5N1QamyD9yOp5kUiuI8YiCjMzLZ1T_pW85QHRoRidTtP-icwa251r5ghSbWsMiYlBqSax9vZM3D3Tj3f77kWi5VvJdvXzeSs8bUAu4ScHTo4Hn1i5wM8gUqfzTfJzgwX5JtyF0k5_3Tc3OcthVavvtEpDWDDYP3Jg-xWTh3ZRWsmQ; SERVERID=e3fa93b0fb9e2e6d4f53273540d4e924|1699186316|1699186310'

    try:
        queue_header.append(('Cookie', cookie))
        ws = CG_Client(
            url="wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
            headers=queue_header,
            ssl_options={
                "cert_reqs": ssl.CERT_NONE
            }
        )
        now = time.time()
        # ws.open_time = now + 1
        ws.queue_start_time = now
        ws.user_name = 'hhh'
        ws.queue_end_time = now + 0.5

        queue_header.append(('Cookie', cookie))
        # time.sleep(5)
        # asyncio.run(queue_pass(ws))
        print('=============================')
        ws.connect()
        print('=============================')

        time.sleep(5)
        start = time.time()

        print('------------------------------')
        ws.run_forever()
        print('------------------------------')

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