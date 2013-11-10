# -*-coding:utf-8 -*-
'''
Created on 2013-10-15

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.contrib import admin
from mail.models import EmailSentCount, EmailWaiting


class EmailAdminBase(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        super(EmailAdminBase, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


class EmailSentCountAdmin(EmailAdminBase):
    actions = ['reset_count']
    list_display = ['email_address', 'email_type', 'count', 'update_time']

    def __init__(self, *args, **kwargs):
        super(EmailSentCountAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def reset_count(self, request, queryset):
        queryset.update(count=0)
    reset_count.short_description = u'重置计数'

    def email_type(self, obj):
        if obj.send_type == 'activation':
            return u'账户激活邮件'
        elif obj.send_type == 'password':
            return u'密码重置邮件'
        return obj.send_type
    email_type.short_description = u'邮件类型'


class EmailWaitingAdmin(EmailAdminBase):
    actions = None
    list_display = ['email_addresses', 'is_sent', 'created']

    def __init__(self, *args, **kwargs):
        super(EmailWaitingAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


admin.site.register(EmailSentCount, EmailSentCountAdmin)
admin.site.register(EmailWaiting, EmailWaitingAdmin)
