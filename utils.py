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

if __name__ == "__main__":
    # send_mail("812487273@qq.com", "0369")
    print(encode("zebra"))
