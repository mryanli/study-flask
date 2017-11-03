#!/usr/bin/python
# -*- coding:UTF-8 -*-
from flask_wtf import Form
from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField

class NameForm(Form):
    name = StringField('Whati is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')
