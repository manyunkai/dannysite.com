# -*-coding:utf-8 -*-
'''
Created on 2013-10-11
@author: Danny<manyunkai@hotmail.com>

Copyright (C) 2012-2014 DannyWork Project
'''

import logging
logger = logging.getLogger('dannysite')


def set_log(level, msg):
    getattr(logger, level)(msg)
