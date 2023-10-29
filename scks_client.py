# import asyncio
# from websockets.sync.client import connect
#
# def hello():
#     with connect("ws://localhost:8765") as websocket:
#         websocket.send("Hello world!")
#         message = websocket.recv()
#         print(f"Received: {message}")
#
# hello()
import json
import asyncio
import pathlib
import ssl
import time
import websockets

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
# ssl_context.load_verify_locations(localhost_pem)

uri = "wss://wechat.v2.traceint.com/ws?ns=prereserve/queue"
# uri = "wss://wechat.v2.traceint.com/ws?ns=prereserve/queue"
queue_header = {
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
    'Cookie': 'Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjMxNjY1NDcwLCJzY2hJZCI6MTI1LCJleHBpcmVBdCI6MTY5NzU1MDg2N30.xHxHdsNMMVe2F5kkOAK4K_EAeDq3mHTNDYjCyFqqZe-BXt_RFag6BagDtiZr-6LTrp3hqlZpfLkk3boUkveWrlimzETzvaa12qShfVhADvnAShWY5-vgtUVi_BW5SQDSCQ1nUpp01sk70Gz5PPCzytjyoA2ImzrE3bGGkeymwXn6YXRLMWX2WFmlRzKa6eBRWqWiPYAfGPWVksM0EDJlnuR14hKmpwb4dj2ZyKfeSYILU0O5kaJNjN69oOivKwHRvDheLEcI6DSeJH7Uhh89PpQ9m38INEvUS5cT_UT2dfrZGby4REaGuYi_8kVbdtoxg0gDcXv56Zb_d0imQrTVEg; SERVERID=e3fa93b0fb9e2e6d4f53273540d4e924|1697543672|1697543667'
}
cnt = 0
start = None
end_time = None
# 创建一个 SSL 上下文并指定协议版本
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def queue_pass():
    start = time.time()
    async with websockets.connect("wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
                                  extra_headers=queue_header,
                                  ssl=ssl_context) as websocket:
        while True:
            try:
                await websocket.send('{"ns":"prereserve/queue","msg":""}')
                ans = await websocket.recv()
                print(ans)
                if ans.find('u6392') != -1:  # 成功排队，2分钟内。。。。
                    print(json.loads(ans)["msg"])
                    break
                elif ans.find('u6210') != -1:  # 已经抢到过座位了
                    print(json.loads(str(ans))["msg"])
                    break
                # json.loads ==> unicode自动转中文
            except Exception as e:
                time.sleep(0.5)
                print(e)
    print('time consumption:', time.time() - start)

if __name__ == "__main__":
    print('1111')
    asyncio.run(queue_pass())
    print('2222')
    print('3333')

    # hello()
