# -*- coding: utf-8 -*-
# ========================================
# Author: wjh
# Date：2020/11/17
# FILE: local
# ========================================
from .base import *

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", 'localhost']

DINGTALK_WEB_HOOK = 'https://oapi.dingtalk.com/robot/send?access_token=0408e0add986f9b5074b06bf571e2fd2aec828f5db31223c88dab769be373355'

INSTALLED_APPS += (
    # other apps for production site
)