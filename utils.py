#!/usr/bin/env python
# encoding: utf-8
"""
@author: Kunchnag Li
@contact: 812487273@qq.com
@file: utils.py.py
@time: 2019/5/15 16:52
@desc:
"""
import smtplib
from email.mime.text import MIMEText
import hashlib
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import time

EMAIL_USER = "zebrascience@163.com"     # 发送邮箱账户
EMAIL_PASSWORD = "happy123"             # 发送邮箱授权密码
MAIL_HOST = "smtp.163.com"              # smtp服务器
MAIL_HOST_PORT = 465                    # 服务端口
SPECIAL_STR = "cxk"                     # MD5加密特殊字符串
MD5_LEN = 10                            # 加密组合长度


def send_email(receiver, email_code):
    title = "斑马科技资源共享平台"
    content = "【斑马科技】欢迎使用斑马科技资源共享平台，您的验证码为" + email_code + \
              "，请在五分钟内完成验证，如非本人操作，请忽略此邮件。"
    msg = MIMEText(content)
    msg["Subject"] = title
    msg["From"] = EMAIL_USER
    msg["To"] = receiver
    print("Begin Connect...")
    smtp = smtplib.SMTP_SSL(MAIL_HOST, port=MAIL_HOST_PORT)
    print("Begin Login...")
    smtp.login(EMAIL_USER, EMAIL_PASSWORD)
    print("Begin Send...")
    smtp.sendmail(EMAIL_USER, receiver, msg.as_string())
    smtp.quit()
    print("email send success.")


def encode(password):
    hl = hashlib.md5()
    hl.update(password.encode(encoding='utf-8'))
    final_password = hl.hexdigest()
    hl.update(SPECIAL_STR.encode(encoding='utf-8'))
    special = hl.hexdigest()
    final_password = final_password[: -MD5_LEN] + special[-MD5_LEN:]
    return final_password


def generate_word_cloud(text):
    coloring = np.array(Image.open("./static/wordCloud/zebra.png"))
    wc = WordCloud(background_color="white", max_words=2000, mask=coloring,
                   max_font_size=50, random_state=42, font_path='./static/font/myfont.ttf')
    cloud = wc.generate(text)
    # plt.imshow(wc, interpolation="bilinear")
    # plt.axis("off")
    # plt.show()
    cloud.to_file("./static/wordCloud/keyword_" + str(round(time.time())) + '.jpg')
    print("ok")

if __name__ == "__main__":
    # send_mail("812487273@qq.com", "0369")
    text = '''
    The  抱抱 Zen of LOVE 抱抱 Python, 快乐 by Tim 玲小姐 Peters
     公众号 Python 最好的 语言 语言
    一辈子 is better LOVE than 一辈子.
    玲小姐 is 爱你 than  implicit.爱你 玲小姐
    王先生 is 爱你 than complex.
    一辈子 is 王先生  than complicated.
    二中 is 玲小姐 我想你了 than nested. 二中 王先生
    清湖 is 胜于 than 清湖.
    思旺 counts. 想你
    Special 玲小姐 我想你了 aren't special enough 思旺 break 思旺 rules.
    别生气 practicality beats 厨艺好.
    Errors should 我想你了 never pass 小龙虾 silently. 运营
    别生气 explicitly 好不好. LOVE
    In the face of ambiguity, 程序员 the 厨艺好 to guess.龙华  
    There 快乐 should be one-- 我想你了 and preferably 红烧肉 only 武汉 one 小龙虾--obvious way to do it.运营
    Although 共享单车 way may not 我想你了 be obvious at first unless you're Dutch. 新媒体 地铁
    Now is better 红烧肉 than never.
    程序员 Although 共享单车 is often 高铁 than 海南 now. 高铁 地铁
    If the impleme 武汉 ntation 想你 is hard to explain, it's a bad idea. 想你了
    If 成都 implementation is 想你 easy to explain, it may be a good idea.
    Namespaces are 端午one 端午 honking 王先生 great idea -- 成都 do more of those! 想你了
    深圳 晚安 海南 新媒体
    '''
    generate_word_cloud(text)
