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

]


def print_que():
    print(queue_header)


def socket_key_random():
    # 生成16字节的随机值
    random_bytes = os.urandom(16)
    # 使用base64编码
    return base64.b64encode(random_bytes).decode('utf-8')
    # print("Sec-WebSocket-Key:", sec_websocket_key)


class CG_Client(WebSocketClient):

    def opened(self):
        self.send('{"ns":"prereserve/queue","msg":""}')
        print('now in queue...')

    def closed(self, code, reason=None):
        print("socket closed down:", code, reason)

    def received_message(self, resp):
        # print('type(resp1):', type(resp))  # type(resp) => class 'ws4py.messaging.TextMessage'
        # unicode转utf-8
        # resp_msg = bytes(str(r"%s" % resp), 'utf-8').decode('unicode_escape')
        # print(resp_msg)
        resp_msg = str(resp)
        if resp_msg.find('u6392') != -1:  # 排队成功返回的第一个字符
            print('queue over')
            self.close()
        elif resp_msg.find('u6210') != -1:  # 已经抢座成功的返回
            print("rsp msg:{}".format(json.loads(resp_msg)["msg"]))
            self.close()
            time.sleep(1)
        else:
            self.opened()


if __name__ == '__main__':
    ws = None
    try:
        ws = CG_Client(
            url="wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
            headers=queue_header
            # ssl_options={}
        )
        cookie = 'Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjMzNTA3NDIxLCJzY2hJZCI6MTI1LCJleHBpcmVBdCI6MTY5NzUyODI1MX0.bWNuRblFuWfNJPg3bLngIjiFjK-gxlQnFzhKxv7MgzmRycCRFEmBVwNIgKmrkGyTtx2Gr4buoHz1iNeEdCFq_tTpGddY0_2-lB_VIKNriIYmzNpzXv2nJMR0GxRHzMEpNpNG6OIVeyEjX1aND7IKod9ZKsmd0liOhAXbB6n-FzCdS2nuOLJ8NNeihH6NnRYWWybElzPWxEHXcpIUzoI_CRN6YcxMtKtXSK4TkvpjcuEFMS0KhwUJNiXJpZCuHUMGYK-auZD9Yy9pFDH6mefcWSJzYdQ3fEhAk65CKT_SkFOon3aYldeocEUsuAA2M8i7PUU8Iln7PHYy3-HO7g0AeQ; SERVERID=e3fa93b0fb9e2e6d4f53273540d4e924|1697521056|1697521051'

        queue_header.append(('Cookie', cookie))
        start = time.time()
        # asyncio.run(queue_pass(ws))
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
