# -*-coding:utf-8 -*-
'''
Created on 2013-12-18

@author: Danny
DannyWork Project
'''

from django.conf.urls import patterns, url

from mail.views import Unsubscribe

urlpatterns = patterns('',
    url(r'^unsubscribe/$', Unsubscribe.as_view(), name='mail_unsubscribe'),
)
