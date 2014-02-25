# -*-coding:utf-8 -*-
'''
Created on 2014-1-15

@author: Danny
DannyWork Project
'''

import os
import time
import binascii

from django.contrib import admin
from django.contrib.admin.util import unquote
from django.conf import settings

from dstore.models import Node
from dstore.forms import FolderForm, FileForm
from dstore.utils import str_crc32


class NodeAdmin(admin.ModelAdmin):
    form = FolderForm
    list_display = ['name', 'type', 'parent', 'is_public', 'dl_url', 'dl_pw']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
            obj.type = 'D' if request.REQUEST.get('type') == 'folder' else 'F'
            obj.icode = str_crc32('-'.join([obj.name, str(time.time())]))
        if obj.type == 'F':
            obj.name = os.path.basename(obj.file.name)
        obj.save()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        self.form = FolderForm if obj and obj.type == 'D' else FileForm
        return super(NodeAdmin, self).change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        self.form = FolderForm if request.REQUEST.get('type') == 'folder' else FileForm
        return super(NodeAdmin, self).add_view(request, form_url, extra_context)

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['parent'].queryset = Node.objects.filter(owner=request.user, type='D')
        return super(NodeAdmin, self).render_change_form(request, context, args, kwargs)

    def dl_url(self, obj):
        if obj.type == 'F':
            url = settings.FILESTORE_DL_URL + obj.icode
            return '<a href="{0}">{1}</a>'.format(url, url)
        return '-'
    dl_url.short_description = u'下载地址'
    dl_url.allow_tags = True

    def dl_pw(self, obj):
        if obj.is_public:
            return u'开放状态，不需要密码'
        return obj.password
    dl_pw.short_description = u'密码'


admin.site.register(Node, NodeAdmin)
