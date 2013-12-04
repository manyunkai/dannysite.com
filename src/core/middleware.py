# -*-coding:utf-8 -*-
'''
Created on 2013-12-4

@author: Danny
DannyWork Project
'''

import urllib2

from django.http.response import HttpResponseRedirect
from django.contrib.sites.models import Site

DESKTOP_SITE_ID = 1
MOBILE_SITE_ID = 2


class BrowserCheckingMiddleware(object):
    def url_unparse(self, scheme, netloc, path, **kwargs):
        return urllib2.urlparse.urlunparse([scheme,
                                            netloc,
                                            path,
                                            kwargs.get('params', ''),
                                            kwargs.get('query', ''),
                                            kwargs.get('fragment', '')])

    def get_return(self, request, mode):
        try:
            mobile, desktop = Site.objects.get(id=MOBILE_SITE_ID), Site.objects.get(id=DESKTOP_SITE_ID)
        except Site.DoesNotExist:
            return None

        if mode == 'desktop' and not request.get_host() == desktop.domain:
            params = {
                'scheme': 'https' if request.is_secure() else 'http',
                'netloc': desktop.domain,
                'path': request.get_full_path()
            }
            return HttpResponseRedirect(self.url_unparse(**params))
        elif mode == 'mobile' and not request.get_host() == mobile.domain:
            params = {
                'scheme': 'https' if request.is_secure() else 'http',
                'netloc': mobile.domain,
                'path': request.get_full_path()
            }
            return HttpResponseRedirect(self.url_unparse(**params))

    def process_request(self, request):
        mode = request.session.get('VIEW_MODE')

        change = request.REQUEST.get('change_view_mode')
        if change and change in ['desktop', 'mobile']:
            mode = change
            request.session['VIEW_MODE'] = mode

        if not mode:
            for key in ['iphone', 'android', 'iemobile']:
                if key in request.META.get('HTTP_USER_AGENT').lower():
                    mode = 'mobile'
                    break
            mode = 'desktop' if not mode else mode
            request.session['VIEW_MODE'] = mode
        #return self.get_return(request, mode)
