# -*-coding:utf-8 -*-
'''
Created on 2013-10-15

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.dispatch import Signal

add_mail = Signal(providing_args=['verb', 'target', 'email', 'site'])
