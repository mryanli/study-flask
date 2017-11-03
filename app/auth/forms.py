#!/usr/bin/python
# -*- coding:UTF-8 -*-

from flask_wtf import Form
from  wtforms import StringField,PasswordField,SubmitField,ValidationError,BooleanField
from wtforms.validators import DataRequired,Length,Email,EqualTo,Regexp
from ..models import User


class LoginForm(Form):
    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember_me=BooleanField()
    submit = SubmitField('Log in')


class RegisterationForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username=StringField('Username',validators=[Regexp('^[A-Za-z0-9_.]*$', 0,
'Usernames must have only letters, '
'numbers, dots or underscores'),Length(4,64),DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('ConfirmPassword', validators=[EqualTo('password',message='Passwords must match.')])
    submit = SubmitField('Register')

    #验证邮箱是否存在
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('this email has been registered')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('this username is in use')

class ChangePasswordForm(Form):
    new_password2 = PasswordField('New Password', validators=[DataRequired()])
    submit=SubmitField('change password')

class ChangeEmailForm(Form):
    new_email = StringField('New Email', validators=[DataRequired(),Email()])
    submit=SubmitField('change email')