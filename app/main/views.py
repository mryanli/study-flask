#!/usr/bin/python
# -*- coding:UTF-8 -*-
import os

from flask import render_template, request, \
    redirect, url_for, session, flash,abort
from datetime import datetime
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm,PostForm
from app.models import User,Role,db,Post
from app.email import send_email
from flask_login import login_required,current_user
from app.decorators import admin_required, permission_required
from app.models import Permission

@main.route('/', methods=['GET', 'POST'])
# @login_required
def index():
    nameform = NameForm()
    if nameform.validate_on_submit():
        user = User.query.filter_by(username=nameform.name.data).first()
        if user is None:
            user = User(username=nameform.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            send_email('346754607@qq.com', 'New User',
                       'mail/new_user', user=user)
        else:
            session['known'] = True
        old_name = session.get('name')
        if old_name is not None and old_name != nameform.name.data:
            flash('looks like you have changed your name')
        session['name'] = nameform.name.data
        nameform.name.data = ''
        return redirect(url_for('main.index'))
    postform = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            postform.validate_on_submit():
        post = Post(body=postform.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', current_time=datetime.utcnow(),
                           nameform=nameform,
                           postform = postform,
                           name=session.get('name'),
                           known=session.get('known', False),
                           posts = posts
                           )


@main.route('/clear/')
def clear():
    session.clear()
    return redirect(url_for('main.index'))


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


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html',user=user,posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.username
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.username = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.username
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)