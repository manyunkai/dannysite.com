# -*-coding:utf-8 -*-
'''
Created on 2014-1-15

@author: Danny
DannyWork Project
'''

from django.conf.urls import patterns, url

from dstore.views import Download

urlpatterns = patterns('',
    url(r'^dl/(\w+)/$', Download.as_view(), name='dstore_dl'),
)
