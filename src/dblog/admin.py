# -*-coding:utf-8 -*-
'''
Created on 2013-10-24

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.contrib import admin
from django.db import models

from dblog.models import Blog, Theme, Category, Tag, Topic
from ueditor.widgets import UEditorWidget
from django.conf import settings


class BlogAdmin(admin.ModelAdmin):
    fields = ['title', 'theme', 'cate', 'topic',
              'content', 'tags', 'is_draft', 'is_published']
    list_display = ['title', 'theme', 'cate', 'author', 'tag_display', 'created',
                    'click_count', 'comment_count', 'is_draft', 'is_published']
    list_editable = ['is_draft', 'is_published']
    list_filter = ['theme__name', 'cate__name', 'is_draft', 'created']
    search_fields = ['title', 'author__username']

    filter_horizontal = ['tags']
    formfield_overrides = {models.TextField: {'widget': UEditorWidget(width=1000, 
                                              file_path='/downloads/', image_path=settings.BLOG_IMAGE_URL,
                                              scrawl_path=settings.BLOG_IMAGE_URL)}}

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()

    def tag_display(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])
    tag_display.short_description = u'标签'


class CAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ['name', 'count', 'created']

admin.site.register(Blog, BlogAdmin)
admin.site.register([Theme, Category, Tag, Topic], CAdmin)
