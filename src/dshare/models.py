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
        verbose_name = u'分类'
        verbose_name_plural = u'分类'


def str_uuid1():
    return str(uuid.uuid1())


def path_and_rename(instance, filename):
    return os.path.join(settings.PHOTO_CONF['origin']['dir'],
                        str_uuid1() + os.path.splitext(filename)[1])


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
