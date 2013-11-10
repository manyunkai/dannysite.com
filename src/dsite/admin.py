# -*-coding:utf-8 -*-
'''
Created on 2013-10-30

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.contrib import admin
from django.db import models

from core.widgets import AdminImageWidget
from dsite.models import Link, Feedback, Focus
from dsite.forms import FocusForm
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['email', 'ip', 'content']


class LinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'desc']
    fields = ['name', 'url', 'desc', 'logo', 'logo_link']
    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget},
    }


class FocusAdmin(admin.ModelAdmin):
    form = FocusForm
    fields = ['title', 'description', 'image']
    list_display = ['title', 'description', 'created', 'shown']
    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget},
    }

    def get_urls(self):
        from django.conf.urls import patterns, url
        info = self.model._meta.app_label, self.model._meta.module_name
        return patterns('',
                        url(r'^(\d+)/shown/$',
                            self.admin_site.admin_view(self.set_shown),
                            name='%s_%s_shown' % info),
                        url(r'^(\d+)/unshown/$',
                            self.admin_site.admin_view(self.set_unshown),
                            name='%s_%s_unshown' % info)
                        ) + super(FocusAdmin, self).get_urls()

    def set_shown(self, request, object_id, from_url=''):
        focus = get_object_or_404(self.queryset(request), pk=object_id)
        focus.is_shown = True
        focus.save()

        return HttpResponseRedirect(from_url or reverse('admin:dsite_focus_changelist'))

    def set_unshown(self, request, object_id, from_url=''):
        focus = get_object_or_404(self.queryset(request), pk=object_id)
        focus.is_shown = False
        focus.save()

        return HttpResponseRedirect(from_url or reverse('admin:dsite_focus_changelist'))

    def shown(self, obj):
        if obj.is_shown:
            return u'<a href="{0}">取消展示</a>'.format(reverse('admin:dsite_focus_unshown', args=[obj.id]))
        return '<a href="{0}">展示</a>'.format(reverse('admin:dsite_focus_shown', args=[obj.id]))
    shown.short_description = u'是否展示'
    shown.allow_tags = True


admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Focus, FocusAdmin)
