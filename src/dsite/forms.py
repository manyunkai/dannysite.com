# -*-coding:utf-8 -*-
'''
Created on 2013-10-30

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django import forms
from django.conf import settings

from captcha.fields import CaptchaField
from dsite.models import Feedback, Focus
from common.image_utils import ModelImageParser, GenericImageParser


class FeedbackForm(forms.ModelForm):
    captcha = CaptchaField(error_messages={'required': u'请填写验证码',
                                           'invalid': u'验证码不正确'})

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.fields['captcha'].widget.attrs['class'] = 'xsmallinput'
        self.fields['captcha'].widget.attrs['placeholder'] = u'输入图中字符'

        self.fields['name'].error_messages = {'required': u'怎么称呼您？'}
        self.fields['email'].error_messages = {'required': u'请填写您的邮箱以便与您联系，我保证一定保密！',
                                               'invalid': u'邮箱格式不正确'}
        self.fields['content'].error_messages = {'required': u'您要反馈什么呀？'}

    class Meta:
        model = Feedback
        fields = ['name', 'email', 'content']
        widgets = {
            'content': forms.Textarea
        }


class FocusForm(forms.ModelForm):
    def clean(self):
        if 'image' in self.changed_data:
            image = self.cleaned_data.get('image', None)
            if image:
                handler = GenericImageParser([image], settings.FOCUS_IMAGE_CONF)
                if not handler.is_valid():
                    self._errors['image'] = self.error_class([handler.error])
            else:
                self._errors['image'] = self.error_class([u'上传的图片无效'])
        return self.cleaned_data

    def save(self, commit=True):
        result = super(FocusForm, self).save(commit=commit)
        result.save()

        if 'image' in self.changed_data:
            handler = ModelImageParser(result.image.path, settings.FOCUS_IMAGE_CONF)
            handler.parse()
            handler.save()

        return result

    class Meta:
        model = Focus
        widgets = {
            'description': forms.Textarea
        }
