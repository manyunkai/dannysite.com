# -*-coding:utf-8 -*-
'''
Created on 2013-11-2

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.conf.urls import patterns, url

from dshare.views import GetShareHome

urlpatterns = patterns('',
    url(r'^$', GetShareHome.as_view(), name='share_home'),
)
