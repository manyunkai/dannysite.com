#coding:utf-8
from django.conf.urls import patterns, url

from ueditor.views import UploadFile, ImageManager, CatchRemoteImage,\
    UploadScrawl, UploadImage

urlpatterns = patterns('',
    url(r'^images/upload/(?P<uploadpath>.*)', UploadImage.as_view(), {'action': 'image'}),
    url(r'^images/list/(?P<imagepath>.*)$', ImageManager.as_view()),
    url(r'^images/fetch/(?P<imagepath>.*)$', CatchRemoteImage.as_view()),
    url(r'^scrawl/upload/(?P<uploadpath>.*)$', UploadScrawl.as_view()),
    url(r'^files/upload/(?P<uploadpath>.*)', UploadFile.as_view()),
)
