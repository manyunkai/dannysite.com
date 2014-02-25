# -*-coding:utf-8 -*-
'''
Created on 2014-1-15

@author: Danny
DannyWork Project
'''

import os

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import pre_save, pre_delete

from user.models import User
from dstore.utils import str_crc32
from common.log_utils import set_log

fs = FileSystemStorage(location=settings.FILESTORE_ROOT,
                       base_url=settings.FILESTORE_DL_NGINX_REDIRECT)


NODE_TYPES = (
    ('D', '文件夹'),
    ('F', '文件')
)


def doc_upload_to(instance, filename):
    return '/'.join([str(instance.owner_id),
                     timezone.now().strftime('%Y%m%d'),
                     str_crc32(filename) + os.path.splitext(filename)[1]])


class Node(models.Model):
    type = models.CharField(u'类型', choices=NODE_TYPES, max_length=1)
    name = models.CharField(u'名字', max_length=100,
                            help_text=u'仅用于文件夹。', blank=True)
    parent = models.ForeignKey('self', verbose_name=u'上一级', null=True, blank=True,
                               help_text=u'关联的文件夹。')
    owner = models.ForeignKey(User, verbose_name=u'上传者')

    file = models.FileField(u'文件', storage=fs, upload_to=doc_upload_to, null=True, blank=True)
    icode = models.CharField(u'标识码', max_length=32)

    is_public = models.BooleanField(u'是否公开')
    password = models.CharField(u'密码', max_length=32, blank=True,
                                help_text=u'当处于非公开状态时，需要输入该密码访问或下载。')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'云盘'
        verbose_name_plural = u'云盘'


def node_pre_save(sender, **kwargs):
    curr = kwargs.get('instance')
    try:
        prev = Node.objects.get(id=curr.id)
    except Node.DoesNotExist:
        pass
    else:
        if not curr.file == prev.file:
            try:
                os.remove(prev.file.path)
            except Exception, e:
                set_log('error', str(e))


def node_pre_delete(sender, **kwargs):
    instance = kwargs.get('instance')
    try:
        os.remove(instance.file.path)
    except Exception, e:
        set_log('error', str(e))

pre_save.connect(node_pre_save, sender=Node)
pre_delete.connect(node_pre_delete, sender=Node)
