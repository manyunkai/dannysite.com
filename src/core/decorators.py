# -*-coding:utf-8 -*-
'''
Created on 2013-11-8

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.conf import settings
from django.http.response import HttpResponseRedirect


def secure_required(view_func):
    """Decorator makes sure URL is accessed over https."""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.is_secure():
            if getattr(settings, 'HTTPS_SUPPORT', True):
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(secure_url)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
