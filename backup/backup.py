# async def queue_pass_websockets(open_time, user):
#     """經過實驗，知道了，即使沒到明日預約開始的時間，仍然可以連接服務器，所以可以省下來連接服務器的時間"""
#     # 创建一个 SSL 上下文并指定协议版本
#     ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#     ssl_context.check_hostname = False
#     ssl_context.verify_mode = ssl.CERT_NONE
#     # queue_header_for_websockets['Cookie'] = User.cookie_dict_to_str_with_equal(
#     #     requests.utils.dict_from_cookiejar(user.session.cookies)
#     # )
#     queue_header_for_websockets['Cookie'] = user.cookie
#     success_pre_reserve = False  # 抢座成功与否的标志
#     async with websockets.connect("wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
#                                   extra_headers=queue_header_for_websockets,
#                                   ssl=ssl_context) as websocket:
#         # 重要！如果不是放在常用座位，需要先请求对应的阅览室的所有座位，libLayout！！
#         # 将访问对应阅览室的请求放在前面，效果一样，缩短抢座所需时间 0.2~0.3s -> 0.05s
#         libLayout_operation['variables']['libId'] = user.lib_id
#         print('name and seats:', user.name, user.seats)
#         """如果排队的时间比较短，可以起到上述的作用，排队时间比较长 比如>10s，则需要在save的时候再重新执行(maybe"""
#         user.session.post(
#             url=url,
#             json=libLayout_operation,  # libLayout
#             verify=False
#         )
#         # 在搶座開始前0.5s就對服務器開始狂轟濫炸???😝
#         start_queue_time = open_time - 0.5
#         end_queue_time = open_time + 0.15
#         print('💥距离开始还有:', open_time - time.time())
#         """时间戳转格式%Y-%m-%d %H:%M:%S"""
#         time_local = time.localtime(open_time)  # 转换成localtime
#         dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)  # 转换成新的时间格式(2016-05-05 20:28:54)
#         print(dt, '的时间戳为：', open_time)
#         # 记录发送的msg的次数（有多少次发送就有多少次返回？）
#         cnt_sent, cnt_recv, save_round = 0, 0, 0
#         name = user.name
#         while True:  # 外循环控制时间
#             if time.time() >= start_queue_time:
#                 while True:  # 内循环控制websocket通信，直到收到排队成功的消息
#                     try:
#                         while start_queue_time <= time.time() <= end_queue_time:
#                             await websocket.send('{"ns":"prereserve/queue","msg":""}')
#                             cnt_sent += 1
#                             print(cnt_sent, name, '>>> msg1', time.time())
#                             # to sleep or not to sleep, that is a question
#                             time.sleep(0.05)
#                         else:
#                             # 没到设定的开始排队的时间，不不要开始，while不成立或者while执行结束就会执行else
#                             if time.time() >= end_queue_time:
#                                 await websocket.send('{"ns":"prereserve/queue","msg":""}')
#                                 cnt_sent += 1
#                                 print(cnt_sent, name, '>>> msg2', time.time())
#                         # 把上面发送的消息所收到的返回接收完
#                         while cnt_sent > 0:
#                             ans = await websocket.recv()
#                             cnt_recv += 1
#                             cnt_sent -= 1
#                             print(cnt_recv, '<<<', time.time(), ans)
#                             if ans.__contains__('u6392'):
#                                 """\u6392排好队的返回， \u6210已经抢完座的返回"""
#                                 success_pre_reserve = seat_save(open_time, user)
#                                 save_round += 1
#                                 print('🎵round', save_round, 'end')
#                                 break
#                         if success_pre_reserve or save_round >= 3:  # 抢座成功或者抢座超过3轮直接退出
#                             return
#                     except Exception as e:
#                         print(e)
#                         if time.time() - open_time >= 60 or save_round >= 5:  # 保证程序退出
#                             break
#                         time.sleep(0.8)
#                 break  # 跳出外层循环
#     if not success_pre_reserve:
#         my_email.goLib_email_info('fail', receiver='2389372927@qq.com')



# async def queue_pass_websockets(open_time, user):
#     """經過實驗，知道了，即使沒到明日預約開始的時間，仍然可以連接服務器，所以可以省下來連接服務器的時間"""
#     # 创建一个 SSL 上下文并指定协议版本
#     ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#     ssl_context.check_hostname = False
#     ssl_context.verify_mode = ssl.CERT_NONE
#     queue_header_for_websockets['Cookie'] = User.cookie_dict_to_str_with_equal(
#         requests.utils.dict_from_cookiejar(user.session.cookies)
#     )
#     # queue_header_for_websockets['Cookie'] = user.cookie
#     success_pre_reserve = False  # 抢座成功与否的标志
#     async with websockets.connect("wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
#                                   extra_headers=queue_header_for_websockets,
#                                   ssl=ssl_context) as websocket:
#         # 重要！如果不是放在常用座位，需要先请求对应的阅览室的所有座位，libLayout！！
#         # 将访问对应阅览室的请求放在前面，效果一样，缩短抢座所需时间 0.2~0.3s -> 0.05s
#         libLayout_operation['variables']['libId'] = user.lib_id
#         print('name and seats:', user.name, user.seats)
#         """如果排队的时间比较短，可以起到上述的作用，排队时间比较长 比如>10s，则需要在save的时候再重新执行(maybe"""
#         user.session.post(
#             url=url,
#             json=libLayout_operation,  # libLayout
#             verify=False
#         )
#         # 在搶座開始前0.5s就對服務器開始狂轟濫炸???😝
#         start_queue_time = open_time - 0.5
#         end_queue_time = open_time + 0.15
#         print('💥距离开始还有:', open_time - time.time())
#         """时间戳转格式%Y-%m-%d %H:%M:%S"""
#         time_local = time.localtime(open_time)  # 转换成localtime
#         dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)  # 转换成新的时间格式(2016-05-05 20:28:54)
#         print(dt, '的时间戳为：', open_time)
#         # 记录发送的msg的次数（有多少次发送就有多少次返回？）
#         cnt_sent, cnt_recv, save_round = 0, 0, 0
#         name = user.name
#         while True:  # 外循环控制时间
#             if time.time() >= start_queue_time:
#                 while True:  # 内循环控制websocket通信，直到收到排队成功的消息
#                     try:
#                         if time.time() >= start_queue_time:
#                             await websocket.send('{"ns":"prereserve/queue","msg":""}')
#                             print(name, '>>> msg', time.time())
#                             ans = await websocket.recv()
#                             print(name, '<<<', time.time(), ans)
#                             if ans.__contains__('u6392'):
#                                 """\u6392排好队的返回， \u6210已经抢完座的返回"""
#                                 success_pre_reserve = seat_save(open_time, user)
#                                 save_round += 1
#                                 print('🎵round', save_round, 'end')
#                             if success_pre_reserve or save_round >= 3:  # 抢座成功或者抢座超过3轮直接退出
#                                 return
#                     except Exception as e:
#                         print(e)
#                         if time.time() - open_time >= 60 or save_round >= 5:  # 保证程序退出
#                             break
#                         time.sleep(0.8)
#                 break  # 跳出外层循环
#     if not success_pre_reserve:
#         my_email.goLib_email_info('fail', receiver='2389372927@qq.com')
