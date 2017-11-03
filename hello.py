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
from flask_script import Shell, Manager
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'hard to guess string'

app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '346754607'
app.config['MAIL_PASSWORD'] = 'poszkqxqkiuibjjd'

db = SQLAlchemy(app)
db.create_all()

manager = Manager(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
moment = Moment(app)
mail = Mail(app)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return "<Role %r>" % self.name


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def _repr_(self):
        return "<Username %r>" % self.username


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


# manager.add_command("shell", Shell(make_context=make_shell_context))
# manager.add_command("db",MigrateCommand)

class NameForm(Form):
    name = StringField('Whati is your name?', validators=[Required()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            send_email('346754607@qq.com', 'New User',
                       'mail/new_user', user=user)
        else:
            session['known'] = True

        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('looks like you have changed your name')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', current_time=datetime.utcnow(),
                           form=form,
                           name=session.get('name'),
                           known=session.get('known', False)
                           )


@app.route('/clear/')
def clear():
    session.clear()
    return redirect(url_for('index'))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(subject, sender=to, recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    with app.app_context():
        thr = Thread(target=send_async_email, args=[app, msg])
        thr.start()
        return thr





if __name__ == '__main__':
    app.run(debug=True)
