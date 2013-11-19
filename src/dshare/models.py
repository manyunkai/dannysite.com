# -*-coding:utf-8 -*-
'''
Created on 2013-11-2

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

import os
import uuid

from django.db import models
from django.conf import settings

from user.models import User


class PhotoCategory(models.Model):
    name = models.CharField(u'类名', max_length=64)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'图片分类'
        verbose_name_plural = u'图片分类'


def str_uuid1():
    return str(uuid.uuid1())


def path_and_rename(instance, filename):
    if type(instance) == Photo:
        path = settings.PHOTO_CONF['origin']['dir']
    elif type(instance) == Share:
        path = settings.SHARE_IMAGE_CONF['origin']['dir']
    return os.path.join(path, str_uuid1() + os.path.splitext(filename)[1])


class Photo(models.Model):
    cate = models.ForeignKey(PhotoCategory, verbose_name=u'类别')
    title = models.CharField(u'标题', max_length=100)
    author = models.CharField(u'作者', max_length=100)
    uploader = models.ForeignKey(User, verbose_name=u'上传者', null=True, blank=True)
    description = models.CharField(u'描述', blank=True, max_length=1000)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    image = models.ImageField(upload_to=path_and_rename, verbose_name=u'照片')
    has_large_size = models.BooleanField(u'支持大尺寸', default=False)
    on_top = models.BooleanField(u'置顶', default=False)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-created']
        verbose_name = u'图片'
        verbose_name_plural = u'图片'


class ShareCategory(models.Model):
    name = models.CharField(u'类名', max_length=64)
    color = models.CharField(u'主题色', max_length=6)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'兴趣分类'
        verbose_name_plural = u'兴趣分类'


class Share(models.Model):
    title = models.CharField(u'标题', max_length=100)
    author = models.ForeignKey(User, verbose_name=u'作者', null=True, blank=True)
    cate = models.ForeignKey(ShareCategory, verbose_name=u'分类')
    cover = models.ImageField(upload_to=path_and_rename, verbose_name=u'封面')
    abstract = models.CharField(u'摘要', max_length=5000)
    content = models.TextField(u'正文', blank=True)
    is_published = models.BooleanField(u'公开状态', default=True)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-created']
        verbose_name = u'兴趣'
        verbose_name_plural = u'兴趣'
