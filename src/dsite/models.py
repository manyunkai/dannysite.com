# -*-coding:utf-8 -*-
'''
Created on 2013-10-30

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

import os
import binascii

from django.db import models
from django.conf import settings

from user.models import User


class Feedback(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, verbose_name=u'用户')
    name = models.CharField(u'称呼', max_length=64)
    email = models.EmailField(u'邮箱')
    ip = models.IPAddressField(u'IP', blank=True)
    content = models.CharField(u'反馈内容', max_length=1000)

    def __unicode__(self):
        return self.email

    class Meta:
        db_table = 'dsite_feedback'
        verbose_name = u'用户反馈'
        verbose_name_plural = u'用户反馈'


def str_crc32(string):
    return(hex(binascii.crc32(string.encode('utf8')))[2:])


def link_image_upload(instance, filename):
    filename = str_crc32(instance.url) + os.path.splitext(filename)[1]
    return os.path.join(settings.LINK_LOGO_ROOT, filename)


class Link(models.Model):
    name = models.CharField(u'显示名称', max_length=50)
    url = models.URLField(u'链接')
    desc = models.CharField(u'描述', max_length=500, null=True, blank=True)
    create_time = models.DateTimeField(u'添加时间', auto_now_add=True)
    logo = models.ImageField(upload_to=link_image_upload, verbose_name=u'站点LOGO', blank=True)
    logo_link = models.URLField(u'LOGO链接', blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'dsite_link'
        verbose_name = u'友情链接'
        verbose_name_plural = u'友情链接'


def focus_image_upload(instance, filename):
    filename = str_crc32(instance.title) + os.path.splitext(filename)[1]
    return os.path.join(settings.FOCUS_IMAGE_ROOT, filename)


class Focus(models.Model):
    title = models.CharField(u'标题', max_length=100)
    image = models.ImageField(upload_to=focus_image_upload, verbose_name=u'配图', blank=True)
    description = models.CharField(u'描述', max_length=1000)
    created = models.DateTimeField(u'添加时间', auto_now_add=True)
    is_shown = models.BooleanField(u'是否展示', default=True)

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = 'dsite_focus'
        verbose_name = u'最近关注'
        verbose_name_plural = u'最近关注'
