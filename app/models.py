#!/usr/bin/python
# -*- coding:UTF-8 -*-
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
import hashlib
from flask import request

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default=db.Column(db.Boolean,default=False,index=True)
    permissions=db.Column(db.Integer)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return "<Role %r>" % self.name



    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.permissions = roles[r][0]
                role.default = roles[r][1]
            db.session.add(role)
            db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class User(UserMixin,db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String,unique=True,index=True)
    username = db.Column(db.String, unique=True)
    password_hash=db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed=db.Column(db.Boolean,default=False)
    activted=db.Column(db.Boolean,default=False)
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow())

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)



    def _repr_(self):
        return "<Username %r>" % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash , password)

    def generate_confirmation_token(self):
        seri=Serializer(current_app.config['SECRET_KEY'],expires_in=3600)
        return seri.dumps({'confirm':self.id})

    def confirm(self,token):
        seri=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=seri.loads(token)
        except:
            return False
        if data.get('confirm') !=self.id:
            return False
        self.confirmed=True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_password(self):
        seri = Serializer(current_app.config['SECRET_KEY'],expires_in=3600)
        return seri.dumps({'resetId':self.id})

    def reset_password(self,token,password):
        seri = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = seri.loads(token)
        except:
            return False
        if data.get('resetId')!=self.id:
            return False
        self.password=password
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_email(self):
        seri = Serializer(current_app.config['SECRET_KEY'],expires_in=3600)
        return seri.dumps({'resetId':self.id})

    def reset_email(self,token,new_email):
        seri = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = seri.loads(token)
        except:
            return False
        if data.get('resetId')!=self.id:
            return False
        self.email=new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()
        return True

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
            hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
            return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default,rating=rating)
