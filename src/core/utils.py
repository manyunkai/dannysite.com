# -*-coding:utf-8 -*-
'''
Created on 2013-10-25

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

import redis


def get_redis():
    return redis.Redis()
