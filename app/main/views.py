#!/usr/bin/python
# -*- coding:UTF-8 -*-
import os
from flask import render_template, request, \
    redirect, url_for, session, flash
from datetime import datetime
from . import main
from .forms import NameForm
from app.models import User,Role,db
from app.email import send_email
from flask_login import login_required
from app.decorators import admin_required, permission_required
from app.models import Permission

@main.route('/', methods=['GET', 'POST'])
# @login_required
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
        return redirect(url_for('main.index'))
    return render_template('index.html', current_time=datetime.utcnow(),
                           form=form,
                           name=session.get('name'),
                           known=session.get('known', False)
                           )


@main.route('/clear/')
def clear():
    session.clear()
    return redirect(url_for('main.index'))


@main.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)



@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"