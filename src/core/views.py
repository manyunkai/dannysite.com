# -*-coding:utf-8 -*-
'''
Created on 2013-3-19

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

import urllib2
import urllib
import binascii
import json

from django.conf import settings
from django.views.generic.base import TemplateResponseMixin, View
from django.http.response import HttpResponseForbidden, HttpResponseServerError,\
    Http404

from core.http import JsonResponse
from common.image_utils import GenericImageParser
from common.log_utils import set_log


def str_crc32(string):
    return(hex(binascii.crc32(string.encode()))[2:])


class BaseView(TemplateResponseMixin, View):
    is_ajax_required = False

    def dispatch(self, request, *args, **kwargs):
        handler = getattr(self, request.method.lower(), None)
        if not request.method.lower() in self.http_method_names or not handler:
            return self.http_method_not_allowed(request)

        if self.is_ajax_required and not request.method == 'GET' and not request.is_ajax():
            return HttpResponseForbidden()

        preloader = getattr(self, 'preloader', None)
        if preloader:
            response = preloader(request, *args, **kwargs)
            if response:
                return response

        return handler(request, *args, **kwargs)


class ImageAutoHandleMixin(object):
    image_handler = GenericImageParser
    image_conf = None
    save_origin = True
    save_dims = True

    files_rev_key = 'pics'

    def get_filename(self):
        return ''

    def auto_handle(self, handler):
        if handler.is_valid() and handler.parse():
            file_name = self.get_filename()
            if file_name:
                if len(handler.parsed) > 1:
                    filenames = [str_crc32(file_name + str(i)) for i in range(len(handler.parsed))]
                else:
                    filenames = [str_crc32(file_name)]
            else:
                filenames = []

            ppics = handler.save(filenames=filenames,
                                 save_origin=self.save_origin,
                                 save_dims=self.save_dims)
            if not ppics:
                set_log('error', handler.sys_error)
                return JsonResponse(status=0, msg=u'发生错误，请重试',
                                    content_type='text/html')

            if hasattr(self, 'after_saving'):
                self.after_saving(ppics)

            return JsonResponse(status=1, data={'images': ppics},
                                content_type='text/html')
        if handler.sys_error:
            set_log('error', handler.sys_error)
        return JsonResponse(status=0, msg=handler.error,
                            content_type='text/html')

    def post(self, request, *args, **kwargs):
        pics = dict(request.FILES).get(self.files_rev_key, [])
        if not pics:
            return JsonResponse(status=0, msg=u'请选择需要上传的图片',
                                content_type='text/html')
        return self.auto_handle(self.image_handler(pics, self.image_conf))


class ImageManualCropMixin(ImageAutoHandleMixin):
    image_handler = None
    image_conf = None
    save_origin = False
    save_dims = True

    def get_crop_location(self, request):
        try:
            x1 = int(request.REQUEST.get("x1").split('.')[0])
            y1 = int(request.REQUEST.get("y1").split('.')[0])
            x2 = int(request.REQUEST.get("x2").split('.')[0])
            y2 = int(request.REQUEST.get("y2").split('.')[0])
            return (x1, y1, x2,  y2)
        except:
            return None

    def post(self, request, *args, **kwargs):
        xy = self.get_crop_location(request)
        if not xy:
            return JsonResponse(status=0, msg=u'还没有选择剪裁范围')

        try:
            image_names = json.loads(request.POST.get('images', ''))
            if not image_names:
                raise Exception()
        except:
            return JsonResponse(status=0, msg=u'不存在可解析的图片')

        return self.auto_handle(self.image_handler(image_names, xy,
                                                   self.image_conf))


class ConnectMixin(object):
    scheme = 'http'
    netloc = ''
    path = ''
    query_dict = {}

    def url_unparse(self, **kwargs):
        return urllib2.urlparse.urlunparse([self.scheme,
                                            self.netloc,
                                            self.path,
                                            kwargs.get('params', ''),
                                            kwargs.get('query', ''),
                                            kwargs.get('fragment', '')])

    def send_request(self):
        req = self.url_unparse(query=urllib.urlencode(self.query_dict))
        try:
            res = urllib2.urlopen(req)
            result = json.loads(res.read())
        except Exception, e:
            set_log('error', e)
            return {}
        else:
            return result


class AccessAuthMixin(object):
    allowed_ips = getattr(settings, 'ALLOWED_IPS', [])

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def is_access_allowed(self, request):
        return self.get_client_ip(request) in self.allowed_ips
