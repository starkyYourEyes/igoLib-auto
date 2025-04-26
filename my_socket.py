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
    # ('Sec-WebSocket-Key', '9999=='), # 这个东西是socket通信自带的，不需要自己加
    ('Sec-WebSocket-Version', '13')
]


class CG_Client(WebSocketClient):
    # open_time = None
    queue_end_time = None
    user_name = None
    sent, recv = 0, 0
    exp = False

    def opened(self):
        while True:  # 到达开始排队的时间以及持续排队的时间
            while time.time() <= self.queue_end_time:
                # 连发，在open_time的前后0.n s内持续发送排队消息。
                self.send('{"ns":"prereserve/queue","msg":""}')
                self.sent += 1
                print(self.sent, f'{self.user_name} >>> msg1', time.time())
                time.sleep(0.05)
            else:
                # 持续时间过了之后，每次只发送一次消息
                if time.time() > self.queue_end_time:
                    self.send('{"ns":"prereserve/queue","msg":""}')
                    self.sent += 1
                    print(self.sent, f'{self.user_name} >>> msg', time.time())
                    break

    def closed(self, code, reason=None):
        print(f"{self.user_name}'s socket closed down:", code, reason)

    def received_message(self, resp):
        resp_msg = str(resp)
        self.recv += 1
        self.sent -= 1
        print(self.recv, f'{self.user_name} <<<', resp_msg, time.time())
        if resp_msg.find('u6392') != -1 or self.recv >= 666:  # 排队成功返回的第一个字符
            print('queue over')
            self.close()
        elif resp_msg.find('u83b7') != -1:
            print(f'{self.user_name}: 获取用户信息失败')
            self.exp = True
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
    cookie = ''

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
    #     'Cookie': 'Autc387432980'
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
