# -*-coding:utf-8 -*-
'''
Created on 2014-1-16

@author: Danny
DannyWork Project
'''

import binascii


def str_crc32(txt):
    return(hex(binascii.crc32(txt.encode('utf8')))[2:])
