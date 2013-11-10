# -*-coding:utf-8 -*-
'''
Created on 2013-11-2

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

import os

from django.contrib import admin
from django.db import models
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from dshare.models import Photo, PhotoCategory
from dshare.forms import PhotoForm
from core.widgets import AdminImageWidget


class PhotoAdmin(admin.ModelAdmin):
    fields = ['cate', 'title', 'author', 'description', 'image']
    form = PhotoForm
    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget},
    }
    list_display = ['image_display', 'title', 'cate',
                    'author', 'created', 'top']
    list_display_links = ['title']

    def image_display(self, obj):
        src = settings.MEDIA_URL + settings.PHOTO_ROOT +\
                      '/'.join(['s250', os.path.basename(obj.image.name)])
        return '<img src="{0}" width=150>'.format(src)
    image_display.short_description = u'图片'
    image_display.allow_tags = True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploader = request.user
        obj.save()

    def get_urls(self):
        from django.conf.urls import patterns, url
        info = self.model._meta.app_label, self.model._meta.module_name
        return patterns('',
                        url(r'^(\d+)/top/$',
                            self.admin_site.admin_view(self.set_top),
                            name='%s_%s_top' % info),
                        url(r'^(\d+)/untop/$',
                            self.admin_site.admin_view(self.set_untop),
                            name='%s_%s_untop' % info)
                        ) + super(PhotoAdmin, self).get_urls()

    def set_top(self, request, object_id, from_url=''):
        photo = get_object_or_404(self.queryset(request), pk=object_id)
        photo.on_top = True
        photo.save()

        return HttpResponseRedirect(from_url or reverse('admin:dshare_photo_changelist'))

    def set_untop(self, request, object_id, from_url=''):
        photo = get_object_or_404(self.queryset(request), pk=object_id)
        photo.on_top = False
        photo.save()

        return HttpResponseRedirect(from_url or reverse('admin:dshare_photo_changelist'))

    def top(self, obj):
        if obj.on_top:
            return u'<a href="{0}">取消置顶</a>'.format(reverse('admin:dshare_photo_untop', args=[obj.id]))
        elif obj.has_large_size:
            return '<a href="{0}">设为置顶</a>'.format(reverse('admin:dshare_photo_top', args=[obj.id]))
        return '该图片不支持置顶图片尺寸'
    top.short_description = u'置顶'
    top.allow_tags = True


class PhotoCategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(Photo, PhotoAdmin)
admin.site.register(PhotoCategory, PhotoCategoryAdmin)
