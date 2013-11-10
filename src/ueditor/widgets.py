#coding:utf-8

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminTextareaWidget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import  conditional_escape
from django.utils.encoding import  force_unicode
from django.utils import simplejson

import settings as u_settings
from utils import make_options


class UEditorWidget(forms.Textarea):
    def __init__(self, width=600, height=300, plugins=(),
                 toolbars=u_settings.DEFAULT_TOOLBARS,
                 file_path='', image_path='', scrawl_path='',
                 image_manager_path='', css='',
                 options={}, attrs=None, **kwargs):
        self.ueditor_options = make_options(width, height, plugins, toolbars,
                                            file_path, image_path, scrawl_path,
                                            image_manager_path, css, options)
        super(UEditorWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        value = '' if value is None else value

        # 取得工具栏设置
        try:
            if type(self.ueditor_options['toolbars']) == list:
                tbar = simplejson.dumps(self.ueditor_options['toolbars'])
            else:
                if getattr(u_settings, 'TOOLBARS_SETTINGS', {})\
                        .has_key(str(self.ueditor_options['toolbars'])):
                    if self.ueditor_options['toolbars'] == 'full':
                        tbar = None
                    else:
                        tbar = simplejson.dumps(u_settings.TOOLBARS_SETTINGS[str(self.ueditor_options['toolbars'])])
                else:
                    tbar = None
        except:
            pass

        # 传入模板的参数
        options = self.ueditor_options.copy()
        options.update({
            'name': name,
            'value': conditional_escape(force_unicode(value)),
            'toolbars': tbar,
            'options': simplejson.dumps(self.ueditor_options['options'])[1:-1]
                #str(self.ueditor_options['options'])[1:-1].replace("True","true").replace("False","false").replace("'",'"')
        })

        context = {
            'UEditor': options,
            'STATIC_URL': settings.STATIC_URL,
            'STATIC_ROOT': settings.STATIC_ROOT,
            'MEDIA_URL': settings.MEDIA_URL,
            'MEDIA_ROOT': settings.MEDIA_ROOT
        }

        return mark_safe(render_to_string('ueditor/ueditor.html', context))

    class Media:
        css = {'all': ('ueditor/themes/default/css/ueditor.css',
                       'ueditor/themes/iframe.css',)}
        js = ('ueditor/ueditor.config.js', 'ueditor/ueditor.all.min.js')


class AdminUEditorWidget(AdminTextareaWidget, UEditorWidget):
    def __init__(self, **kwargs):
        self.ueditor_options = kwargs
        super(UEditorWidget, self).__init__(kwargs)
