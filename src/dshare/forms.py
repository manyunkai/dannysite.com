# -*-coding:utf-8 -*-
'''
Created on 2013-11-2

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django import forms
from django.conf import settings

from dshare.models import Photo, Share
from common.image_utils import ModelImageParser, GenericImageParser
from ueditor.widgets import UEditorWidget


class PhotoForm(forms.ModelForm):
    def clean(self):
        if 'image' in self.changed_data:
            image = self.cleaned_data.get('image', None)
            if image:
                handler = GenericImageParser([image], settings.PHOTO_CONF)
                if not handler.is_valid():
                    self._errors['image'] = self.error_class([handler.error])
            else:
                self._errors['image'] = self.error_class([u'上传的图片无效'])
        return self.cleaned_data

    def save(self, commit=True):
        result = super(PhotoForm, self).save(commit=commit)
        result.save()

        if 'image' in self.changed_data:
            handler = ModelImageParser(result.image.path, settings.PHOTO_CONF)
            handler.parse()
            handler.save()

            if handler.parsed.size[0] > 950:
                result.has_large_size = True
            else:
                result.has_large_size = False
            result.save()

        return result

    class Meta:
        model = Photo
        widgets = {
            'description': forms.Textarea
        }


class FocusForm(forms.ModelForm):
    def clean(self):
        if 'cover' in self.changed_data:
            image = self.cleaned_data.get('cover', None)
            if image:
                handler = GenericImageParser([image], settings.SHARE_IMAGE_CONF)
                if not handler.is_valid():
                    self._errors['cover'] = self.error_class([handler.error])
            else:
                self._errors['cover'] = self.error_class([u'上传的图片无效'])
        return self.cleaned_data

    def save(self, commit=True):
        result = super(FocusForm, self).save(commit=commit)
        result.save()

        if 'cover' in self.changed_data:
            handler = ModelImageParser(result.cover.path, settings.SHARE_IMAGE_CONF)
            handler.parse()
            handler.save()

        return result

    class Meta:
        model = Share
        widgets = {
            'abstract': forms.Textarea,
            'content': UEditorWidget(width=1000,
                                     file_path='/downloads/',
                                     image_path=settings.SHARE_UPLOADED_IMAGE_URL,
                                     scrawl_path=settings.SHARE_UPLOADED_IMAGE_URL)
        }
