#!/usr/bin/python
# -*- coding:UTF-8 -*-

from flask import Blueprint

main = Blueprint('main', __name__)

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

import views, errors, forms