import json
import random
import time
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import requests
from lxml import etree
from typing import Union
ua_pool = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.4) Gecko/20100503 Firefox/3.6.4 ( .NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; nb-NO; rv:1.9.2.4) Gecko/20100611 Firefox/3.6.4 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; ko; rv:1.9.2.4) Gecko/20100523 Firefox/3.6.4',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; cs; rv:1.9.2.4) Gecko/20100611 Firefox/3.6.4',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.3pre) Gecko/20100405 Firefox/3.6.3plugin1 ( .NET CLR 3.5.30729)',
    'Mozilla/5.0 (X11; U; Linux x86_64; fr; rv:1.9.2.3) Gecko/20100403 Fedora/3.6.3-4.fc13 Firefox/3.6.3',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.3) Gecko/20100403 Firefox/3.6.3',
    'Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.2.3) Gecko/20100401 SUSE/3.6.3-1.1 Firefox/3.6.3',
    'Mozilla/5.0 (X11; U; Linux i686; ko-KR; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.3) Gecko/20100404 Ubuntu/10.04 (lucid) Firefox/3.6.3',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 GTB7.1',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.3',
    'Mozilla/5.0 (X11; U; Linux i686; de; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3',
    'Mozilla/5.0 (X11; U; Linux AMD64; en-US; rv:1.9.2.3) Gecko/20100403 Ubuntu/10.10 (maverick) Firefox/3.6.3',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; pl; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; it; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; hu; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 GTB7.1',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; es-ES; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 GTB7.1',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; es-ES; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 GTB7.0 ( .NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; es-ES; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; cs; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; ca; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (X11; U; Linux i686; fr; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; fr; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2 GTB7.0',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.2) Gecko/20100316 AskTbSPC2/3.9.1.14019 Firefox/3.6.2',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2 ( .NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; pl; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2 GTB6 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2 ( .NET CLR 3.0.04506.648)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2 ( .NET CLR 3.0.04506.30)',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.7; en-US; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.10pre) Gecko/20100902 Ubuntu/9.10 (karmic) Firefox/3.6.1pre',
    'Mozilla/5.0 (X11; U; Linux x86_64; ja-JP; rv:1.9.2.16) Gecko/20110323 Ubuntu/10.10 (maverick) Firefox/3.6.16',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.16) Gecko/20110323 Ubuntu/9.10 (karmic) Firefox/3.6.16 FirePHP/0.5',
    'Mozilla/5.0 (X11; U; Linux i686; en-GB; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.16'
]


def daily_poem():
    tree = etree.HTML(requests.get(
        url='https://meirishici.com/poetry/dailies',
        headers={
            'User-Agent': ua_pool[random.randint(0, len(ua_pool) - 1)]
        }
    ).text)
    title = tree.xpath('//*[@id="app"]/div/main/div[1]/div[1]/h2/a/text()')[0]
    author = "".join(tree.xpath('//*[@id="app"]/div/main/div[1]/div[1]/div[2]//text()'))
    content = tree.xpath('//*[@id="app"]/div/main/div[1]/div[1]/div[3]/text()')[0]
    return {
        "title": title,
        "author": author,
        "content": content
    }


# ??
# smtplib模块主要负责发送邮件：是一个发送邮件的动作，连接邮箱服务器，登录邮箱，发送邮件（有发件人，收信人，邮件内容）。
# email模块主要负责构造邮件：指的是邮箱页面显示的一些构造，如发件人，收件人，主题，正文，附件等。
def goLib_email_info(msg_server, mail_content='default info'):
    time.sleep(5 * random.random())
    host_server = 'smtp.qq.com'  # qq邮箱smtp服务器
    sender_qq = '1702305010@qq.com'  # 发件人邮箱 2389372927@qq.com
    pwd = 'xzzuywjvscmzehae'  # omnafobylbzfeaci
    receiver = ['2389372927@qq.com']  # 收件人邮箱
    # receiver = '913@qq.com'
    mail_title = '我去图书馆——明日预约通知'  # 邮件标题
    seat_info = ''
    if type(mail_content) == dict:
        seat_info += mail_content['data']['userAuth']['prereserve']['prereserve']['lib_name'] + ', '
        seat_info += mail_content['data']['userAuth']['prereserve']['prereserve']['seat_name'] + '号座位。'

    if msg_server == 'success':
        con = daily_poem()
        con['content'] = con['content'].replace(f'\r\n', '<br>')

        mail_content = f"""
        <html class="h-screen " lang="zh-">
        <meta charset="utf-8" />
        恭喜，明日预约成功！预约信息: {seat_info}<br>
        每日诗词：
        <div class="text-center card">
          <p style="text-align:center; font-size:21px; font-family:STKaiti,serif">
            {con['title']}
          </p> 
          <p class="mb-10" style="text-align:center; font-size:18px; font-family:Simsun,serif">
            {con['author']}
          </p>
          <div style="text-align:center; font-size:18px; font-family:Simsun,serif">
            {con['content']}
          </div>
        </div>
        </html>
        """  # 邮件正文内容
    elif msg_server == 'fail':
        mail_title = '我去图书馆——明日预约失败'
        mail_content = "糟糕，本次预约失败了呢。。。"  # 邮件正文内容
    elif msg_server == 'error':
        mail_title = '我去图书馆——运行出错'
        mail_content = "程序运行出错。。。"  # 邮件正文内容
    elif msg_server == 'SessionError':
        mail_title = '我去图书馆——运行出错'
        mail_content = """
        <img src="https://img.ikarox.cn/i/2023/10/09/ne4902.png"></img>
        """

    # 初始化一个邮件主体
    msg = MIMEMultipart()
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_qq
    # msg["To"] = Header("测试邮箱",'utf-8')
    msg['To'] = ";".join(receiver)
    # 邮件正文内容
    msg.attach(MIMEText(mail_content, 'html', 'utf-8'))

    smtp = SMTP_SSL(host_server)  # ssl登录

    # login(user,password):
    # user:登录邮箱的用户名。
    # password：登录邮箱的密码，像笔者用的是网易邮箱，网易邮箱一般是网页版，需要用到客户端密码，需要在网页版的网易邮箱中设置授权码，该授权码即为客户端密码。
    smtp.login(sender_qq, pwd)

    # sendmail(from_addr,to_addrs,msg,...):
    # from_addr:邮件发送者地址
    # to_addrs:邮件接收者地址。字符串列表['接收地址1','接收地址2','接收地址3',...]或'接收地址'
    # msg：发送消息：邮件内容。一般是msg.as_string():as_string()是将msg(MIMEText对象或者MIMEMultipart对象)变为str。
    smtp.sendmail(sender_qq, receiver, msg.as_string())

    # quit():用于结束SMTP会话。
    smtp.quit()


if __name__ == '__main__':
    goLib_email_info('success')
