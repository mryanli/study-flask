#!/usr/bin/python
# -*- coding:UTF-8 -*-
import os
from flask import Flask, render_template, request, \
    redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import Form
from wtforms.validators import Required
from wtforms import StringField, SubmitField
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell,Manager
from flask_migrate import Migrate,MigrateCommand

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)





app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

migrate=Migrate(app,db)
manager=Manager(app)


# manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db",MigrateCommand)


