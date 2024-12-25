import random
import re
import time
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import requests
from lxml import etree


ua_pool = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.4) Gecko/20100503 Firefox/3.6.4 ( .NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; nb-NO; rv:1.9.2.4) Gecko/20100611 Firefox/3.6.4 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; ko; rv:1.9.2.4) Gecko/20100523 Firefox/3.6.4',
    'Mozilla/5.0 (X11; U; Linux x86_64; fr; rv:1.9.2.3) Gecko/20100403 Fedora/3.6.3-4.fc13 Firefox/3.6.3',
    'Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.2.3) Gecko/20100401 SUSE/3.6.3-1.1 Firefox/3.6.3'
]
festival = []


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
    ct_date = tree.xpath('//*[@id="app"]/div/main/div[1]/div[1]/div[1]/div[2]/text()')[0]
    return {
        "title": title,
        "author": author,
        "content": content,
        "date": ct_date
    }


def festival_to_come():
    global festival
    classical_fes = ['元旦', '春节', '清明节', '劳动节', '五四青年节', '高考', '端午节', '母亲节', '父亲节', '中秋节', '国庆节']
    tree = etree.HTML(requests.get(
        url='https://www.daojishi321.com/',
        headers={
            'User-Agent': ua_pool[random.randint(0, len(ua_pool) - 1)]
        }
    ).text)
    fes = tree.xpath("/html/body/div[1]/div[2]/div/div[3]/div[2]/ul/li")
    for li in fes:
        name = li.xpath("./div/div[1]/a/text()")[0]
        if name in classical_fes:
            t = li.xpath("./div/div[2]/div/span[1]/text()")[0]
            assert name is not None and name != '' and t is not None and t != ''
            festival = [name, t]
            break

# smtplib模块主要负责发送邮件：是一个发送邮件的动作，连接邮箱服务器，登录邮箱，发送邮件（有发件人，收信人，邮件内容）。
# email模块主要负责构造邮件：指的是邮箱页面显示的一些构造，如发件人，收件人，主题，正文，附件等。
def goLib_email_info(msg, mail_content='default info', receiver=None):
    receiver = receiver if receiver is not None and receiver.strip(' ') != "" else '927@qq.com'
    regex = re.compile(r'[1-9]\d+@qq.com')  # 默认为qq邮箱
    if not re.fullmatch(regex, receiver):
        print(receiver, "this receiver string is invalid qqmail address!")
        receiver = '927@qq.com'

    time.sleep(3 * random.random())
    host_server = 'smtp.qq.com'  # qq邮箱smtp服务器

    sender_qq = '170@qq.com'  # 发件人邮箱 
    pwd = ''  #  smtp 密钥

    mail_title = '你去图书馆——明日预约'  # 邮件标题
    seat_info = '预约信息: '
    if type(mail_content) == dict:
        seat_info += mail_content['data']['userAuth']['prereserve']['prereserve']['lib_name'] + ', '
        seat_info += mail_content['data']['userAuth']['prereserve']['prereserve']['seat_name'] + '号座位。'
    else:
        seat_info = ''

    if msg == 'success':
        try:
            con = daily_poem()
        except Exception as e:
            con = {
                'content': '',
                'title': '',
                'author': '',
                'date': ''
            }
            print('error in daily poem!')
            print(e)
        con['content'] = con['content'].replace(f'\r\n', '<br>')
        mail_content = f"""
        <html class="h-screen " lang="zh-">
        <meta charset="utf-8" />
        <div style="display: flex; font-size: 16px">
            <div style="width: 50%">
            恭喜，明日预约成功！
            </div>
            <div style="width: 50%; text-align: right; font-weight: bold">
            {con['date']}
            </div>
        </div>
        <div style="font-size: 16px">
        {seat_info}
        </div>
        <div>
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
        <br>
        </html>
        """  # 邮件正文内容
        # <div style="font-size:16px; text-align: right; font-family:STZhongsong">
        #     距离{festival[0]}还有{festival[1]}天
        # </div>
    elif msg == 'fail':
        mail_title = '我去图书馆——明日预约失败'
        mail_content = "糟糕，本次预约失败了呢。。。"  # 邮件正文内容
    elif msg == 'error':
        mail_title = '我去图书馆——运行出错'
        mail_content = "程序运行出错。。。"  # 邮件正文内容
    elif msg == 'SessionError':
        mail_title = '我去图书馆——cookie失效'
        mail_content = """
        <img src=""></img>
        """
    else:
        mail_content = 'unknown message'

    msg = MIMEMultipart()  # 初始化一个邮件主体
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_qq
    msg['To'] = receiver
    msg.attach(MIMEText(mail_content, 'html', 'utf-8'))  # 邮件正文内容

    smtp = SMTP_SSL(host_server)  # ssl登录
    smtp.login(sender_qq, pwd)
    smtp.sendmail(sender_qq, receiver, msg.as_string())
    print('email already sent to', receiver, time.ctime())
    smtp.quit()  # 结束当前SMTP会话


if __name__ == '__main__':
    # festival_to_come()
    festival_to_come()
    goLib_email_info('success', '123')
    time.sleep(0.4)
    # goLib_email_info('success', '123')
