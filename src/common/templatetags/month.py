# -*-coding:utf-8 -*-
'''
Created on 2013-11-6
@author: Danny<manyunkai@hotmail.com>

Copyright (C) 2012-2014 DannyWork Project
'''

from django import template
from django.utils import timezone

register = template.Library()


@register.tag
def get_month(value):
    return timezone.localtime(value).strftime('%b')

register.filter('month', get_month)
