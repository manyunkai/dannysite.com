# -*-coding:utf-8 -*-
'''
Created on 2013-10-30

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            output.append('<a href="%s" target="_blank"><img src="%s" width=200 /></a>'
                          % (image_url, image_url))
        output.append(super(AdminFileWidget,
                            self).render(name, value, attrs))
        return mark_safe(u''.join(output))
