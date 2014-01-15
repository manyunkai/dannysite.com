# -*-coding:utf-8 -*-
'''
Created on 2014-1-15

@author: Danny
DannyWork Project
'''

import os

from django.views.generic.base import TemplateView
from django.http.response import Http404, HttpResponse

from dstore.models import Node


class Download(TemplateView):
    template_name = 'dstore/dl.html'

    def dl_redirect(self, node):
        response = HttpResponse()
        response['Content-Type'] = 'application/octet-stream'
        response['X-Accel-Redirect'] = node.file.url
        response['Content-Disposition'] = 'attachment; filename={0}'.format(os.path.basename(node.file.name))
        return response

    def get(self, request, icode):
        try:
            node = Node.objects.get(type='F', icode=icode)
        except Node.DoesNotExist:
            raise Http404

        if node.is_public or node.owner == request.user:
            return self.dl_redirect(node)

        return self.render_to_response({'node': node})

    def post(self, request, icode):
        try:
            node = Node.objects.get(type='F', icode=icode)
        except Node.DoesNotExist:
            raise Http404

        if node.is_public or node.password == request.POST.get('password') or node.owner == request.user:
            return self.dl_redirect(node)

        return self.render_to_response({'node': node, 'pw_incorrect': True})
