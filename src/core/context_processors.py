# -*-coding:utf-8 -*-
'''
Created on 2013-12-4

@author: Danny
DannyWork Project
'''


def device_info(request):
    context = {}
    for key in ['iphone', 'android', 'iemobile']:
        if key in request.META.get('HTTP_USER_AGENT').lower():
            context['is_mobile'] = True
    context['is_mobile'] = False if not context.get('is_mobile') else context['is_mobile']

    return context
