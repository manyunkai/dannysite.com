# -*-coding:utf-8 -*-
'''
Created on 2013-10-24

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django import forms
from django.contrib.contenttypes.models import ContentType

from captcha.fields import CaptchaField
from core.models import DComment


class CommentForm(forms.ModelForm):
    captcha = CaptchaField(error_messages={'required': u'请填写验证码',
                                           'invalid': u'验证码不正确'})

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['captcha'].widget.attrs['class'] = 'xsmallinput'
        self.fields['captcha'].widget.attrs['placeholder'] = u'输入图中字符'

        self.fields['user_name'].required = True
        self.fields['user_name'].error_messages = {'required': u'怎么称呼您？'}

        self.fields['user_email'].required = True
        self.fields['user_email'].error_messages = {'required': u'请填写您的邮箱，我保证一定保密！',
                                                    'invalid': u'邮箱格式不正确'}
        self.fields['user_url'].error_messages = {'invalid': u'个人网站格式不正确（注：以协议开头，如http）'}
        self.fields['comment'].error_messages = {'required': u'请输入您的留言'}

    def save(self, blog, ip, site, commit=True):
        obj = super(CommentForm, self).save(commit=False)
        obj.ip_address = ip
        obj.site = site
        obj.content_type = ContentType.objects.get_for_model(blog)
        obj.object_pk = blog.pk

        if commit:
            obj.save()

        return obj

    class Meta:
        model = DComment
        fields = ['user_name', 'user_email', 'user_url', 'comment', 'related']
        widgets = {'related': forms.HiddenInput}
