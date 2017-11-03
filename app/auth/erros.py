#!/usr/bin/python
# -*- coding:UTF-8 -*-

from . import auth
from flask import render_template,url_for


@auth.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404