# -*-coding:utf-8 -*-
'''
Created on 2013-11-2

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.conf.urls import patterns, url

from dshare.views import GetPhotoHome

urlpatterns = patterns('',
    url(r'^$', GetPhotoHome.as_view(), name='photo_home'),
)
