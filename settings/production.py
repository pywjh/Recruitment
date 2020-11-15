# -*- coding: utf-8 -*-
# ========================================
# Author: wjh
# Date：2020/11/15
# FILE: product
# ========================================
"""
线上环境的时候，使用python manage.py runserver x.x.x.x:xxxx --settings=settings.production
"""
from .base import *

DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1"]

INSTALLED_APPS += (
    # other apps for production site
)