# -*-coding:utf-8 -*-
'''
Created on 2013-7-29
@author: Danny<manyunkai@hotmail.com>

Copyright 2012-2014 DannyWork Project
'''

import os

from common.log_utils import set_log


def is_file_exist(path):
    '''判断文件或目录是否存在'''
    if os.path.exists(path):
        return True
    return False


def remove(path, filename):
    '''remove file from the filesystem'''
    if not filename:
        return False

    fullpath = os.path.join(path, filename)
    try:
        os.remove(fullpath)
        return True
    except OSError:
        set_log('info', "delete file %s error" % fullpath)
        return False
