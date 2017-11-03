#!/usr/bin/python
# -*- coding:UTF-8 -*-
from flask import render_template, redirect, request, url_for, flash
from . import auth
from flask_login import login_user
from ..models import User
from .forms import LoginForm, RegisterationForm,ChangePasswordForm,ChangeEmailForm
from flask_login import login_required, current_user, logout_user
from .. import db
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('invalid email or password')
    return render_template('auth/login.html', form=form)


@auth.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        token = user.generate_confirmation_token()
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, "Confirm your Registering", 'mail/confirm', user=user, token=token)
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash('You have confirmed your account. Thanks!')
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))



@auth.route('/confirm')
@login_required
def reconfirm():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'mail/confirm', user=current_user, token=token)
    flash('Ab new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))



@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/change-password/')
@login_required
def change_password_email():
    flash('We have send you a email,please click the link in your email to reset your password')
    str=dir(current_user)
    token=current_user.generate_reset_password()
    send_email(current_user.email,"To change your password",'mail/change_password',user=current_user,token=token)
    return render_template('auth/before_chpw.html')


@auth.route('/change-password/<token>',methods=['GET','POST'])
def change_password(token):
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.reset_password(token,form.new_password2.data):
            flash('you have changed your password')
            return redirect(url_for('main.index'))
        else:
            flash('sorry,you are not authenrated to change this accounts password' )
            return redirect(url_for('main.index'))
    return render_template('auth/change_password.html',form=form)

@auth.route('/change-email/')
@login_required
def change_email_email():
    flash('We have send you a email,please click the link in your email to reset your emailaddress')
    str=dir(current_user)
    token=current_user.generate_reset_email()
    send_email(current_user.email,"To change your email",'mail/change_email',user=current_user,token=token)
    return render_template('auth/before_ch_email.html')


@auth.route('/change-email/<token>',methods=['GET','POST'])
def change_email(token):
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.reset_email(token,form.new_email.data):
            flash('you have changed your email')
            return redirect(url_for('main.index'))
        else:
            flash('sorry,you are not authenrated to change this accounts email' )
            return redirect(url_for('main.index'))
    return render_template('auth/change_email.html',form=form)