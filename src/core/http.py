# -*-coding:utf-8 -*-
'''
Created on 2013-2-25

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.http.response import HttpResponse
import json


class JsonResponse(HttpResponse):
    def __init__(self, status, msg='', data={},
                 content_type='application/json', *args, **kwargs):
        data['status'] = status
        if msg:
            data['message'] = msg

        super(JsonResponse, self).__init__(json.dumps(data),
                                           content_type=content_type,
                                           *args, **kwargs)
