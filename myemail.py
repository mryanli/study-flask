#!/usr/bin/python
# -*- coding:UTF-8 -*-
import os
from flask_mail import Mail,Message
from flask import Flask




app=Flask(__name__)

app.config['MAIL_SERVER']='smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '346754607'
app.config['MAIL_PASSWORD'] = 'poszkqxqkiuibjjd'

mail=Mail(app)


msg=Message("hello",sender="346754607@qq.com",recipients=['346754607@qq.com'])
msg.body="nihao"
msg.html="<p1>haha</p1>"

with app.app_context():
    mail.send(msg)