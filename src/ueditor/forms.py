#coding: utf-8

from django import forms
import settings as u_settings

from widgets import UEditorWidget
from utils import make_options


class UEditorField(forms.CharField):
    def __init__(self, label, width=600, height=300, plugins=(),
                 toolbars=u_settings.DEFAULT_TOOLBARS, file_path='',
                 image_path='', scrawl_path='', image_manager_path='',
                 css='', options={}, *args, **kwargs):
        options = make_options(width, height, plugins, toolbars,
                               file_path, image_path, scrawl_path,
                               image_manager_path, css, options)

        kwargs['widget'] = UEditorWidget(**options)
        kwargs['label'] = label

        super(UEditorField, self).__init__(*args, **kwargs)


def UpdateUploadPath(widget, model_inst=None):
    try:
        from models import UEditorField as ModelUEditorField

        for field in model_inst._meta.fields:
            if isinstance(field, ModelUEditorField):
                if callable(field.ueditor_options['o_image_path']):
                    new_path = field.ueditor_options["o_image_path"](model_inst)
                    widget.__getitem__(field.name).field.widget.ueditor_options['image_path'] = new_path
                    if field.ueditor_options['o_image_manager_path'] == '':
                        widget.__getitem__(field.name).field.widget.ueditor_options['image_manager_path'] = new_path
                    if field.ueditor_options['o_scrawl_path'] == '':
                        widget.__getitem__(field.name).field.widget.ueditor_options['scrawl_path'] = new_path
                if callable(field.ueditor_options['o_file_path']):
                    widget.__getitem__(field.name).field.widget.ueditor_options['file_path'] = field.ueditor_options['o_file_path'](model_inst)
                if callable(field.ueditor_options['o_image_manager_path']):
                    widget.__getitem__(field.name).field.widget.ueditor_options['image_manager_path'] =field.ueditor_options['o_image_manager_path'](model_inst)
                if callable(field.ueditor_options['o_scrawl_path']):
                    widget.__getitem__(field.name).field.widget.ueditor_options['scrawl_path'] =field.ueditor_options['o_scrawl_path'](model_inst)
    except:
        pass


class UEditorModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UEditorModelForm, self).__init__(*args, **kwargs)
        try:
            if kwargs.has_key('instance'):
                UpdateUploadPath(self, kwargs['instance'])
            else:
                UpdateUploadPath(self, None)
        except Exception:
            pass
