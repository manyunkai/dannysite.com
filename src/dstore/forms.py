# -*-coding:utf-8 -*-
'''
Created on 2014-1-15

@author: Danny
DannyWork Project
'''

from django import forms

from dstore.models import Node


class FolderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FolderForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True

    def clean(self):
        if not self.cleaned_data.get('is_public') and not self.cleaned_data.get('password'):
            self._errors['password'] = self.error_class([u'非公开状态下，密码是必须的。'])
        return self.cleaned_data

    class Meta:
        model = Node
        fields = ('name', 'parent', 'is_public', 'password')


class FileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = True

    def clean(self):
        if not self.cleaned_data.get('is_public') and not self.cleaned_data.get('password'):
            self._errors['password'] = self.error_class([u'非公开状态下，密码是必须的。'])
        return self.cleaned_data

    class Meta:
        model = Node
        fields = ('parent', 'file', 'is_public', 'password')
