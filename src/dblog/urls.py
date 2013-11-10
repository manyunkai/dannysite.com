# -*-coding:utf-8 -*-
'''
Created on 2013-10-24

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.conf.urls import patterns, url

from dblog.views import GetHome, GetDetail, Comment, OldDetail
from dblog.feeds import LatestBlogs

urlpatterns = patterns('',
    url(r'^$', GetHome.as_view(), name='blog_home'),
    url(r'^detail/$', OldDetail.as_view(), name='old_style_detail'),
    url(r'^(\d+)/$', GetDetail.as_view(), name='blog_detail'),
    url(r'^(\d+)/comment/$', Comment.as_view(), name='blog_comment'),
    url(r'^rss/$', LatestBlogs(), name='blog_rss'),
)
