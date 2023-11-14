    if not success_pre_reserve:
        my_email.goLib_email_info('fail', receiver='2389372927@qq.com')
- 上面receiver(抢座失败的话，只给自己发送信息，成功才给别人发。)，preserve_seat_tomorrow.py,line 189
- my_email功能完善一下
- 尝试ws4py的多线程抢座。11.4, test 3 users ok !? 11.5, test 5 users ok!!

