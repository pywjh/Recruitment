# -*- coding: utf-8 -*-
# ========================================
# Author: wjh
# Date：2020/11/12
# FILE: urls
# ========================================

from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # 首页自动跳转到 职位列表
    url(r"^$", views.joblist, name="index"),
    url(r"^joblist/", views.joblist, name="joblist"),
    url(r'^job/(?P<job_id>\d+)/$', views.job_detail, name='job_detail'),
    path('resume/add/', views.ResumeView.as_view(), name='resume_add'),
    path('resume/<int:pk>/', views.resume_detail, name='resume_detail'),
]