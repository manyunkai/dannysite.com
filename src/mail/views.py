# -*-coding:utf-8 -*-
'''
Created on 2013-12-18

@author: Danny
DannyWork Project
'''

from django.views.generic.base import TemplateView
from django.core.exceptions import PermissionDenied

from mail.models import EmailWaiting


class Unsubscribe(TemplateView):
    template_name = 'info.html'

    def get(self, request):
        sn = request.GET.get('sn', '').lower()
        mail = request.GET.get('m')

        try:
            obj = EmailWaiting.objects.get(sn=sn)
        except EmailWaiting.DoesNotExist:
            raise PermissionDenied

        context = {}
        if obj.related_object_content_type.model == 'dcomment' and obj.email_addresses == mail:
            comment = obj.related_object.related
            if comment.mail_reply:
                comment.mail_reply = False
                comment.save()
                context['info'] = u'已成功退订，感谢您对DannySite的支持！'
            else:
                context['info'] = u'您已退订，无需重复提交，感谢您对DannySite的支持！'
        else:
            raise PermissionDenied

        context['title'] = '邮件退订提醒'
        return self.render_to_response(context)
