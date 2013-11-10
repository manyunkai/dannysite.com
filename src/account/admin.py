# -*-coding:utf-8 -*-
'''
Created on 2013-10-24

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.contrib import admin

from account.models import EmailAddress, SignupCode
from django.contrib.auth.models import Permission
from django.utils import timezone


class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ['user', 'temp_key', 'timestamp', 'reset']


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'verified', 'primary']


class SignupCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'inviter', 'invite_status', 'valid_status', 'created']
    fields = ['email', 'notes', 'expiry', 'max_uses']

    def __init__(self, *args, **kwargs):
        super(SignupCodeAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def invite_status(self, obj):
        value = unicode(obj.email) if obj.email else u'未定义'
        value += u'（邀请邮件已投递到对方邮箱）' if obj.email and obj.sent else u''
        return value
    invite_status.short_description = u'受邀者'

    def valid_status(self, obj):
        if obj.use_count >= obj.max_uses:
            return u'已失效'
        if obj.expiry and timezone.now() <= obj.expiry:
            return u'已过期'
        return u'有效（剩余{0}次）'.format(obj.max_uses - obj.use_count)
    valid_status.short_description = u'邀请码状态'

    def save_model(self, request, obj, form, change):
        if not obj.code:
            obj.generate_code()
        obj.inviter = request.user if not obj.inviter else obj.inviter
        obj.save()


from django.utils.translation import ugettext_lazy

ERROR_MESSAGE = ugettext_lazy("Please enter a correct username and password. "
                              "Note that both fields are case-sensitive.")


admin.site.register(Permission)
admin.site.register(EmailAddress, EmailAddressAdmin)
admin.site.register(SignupCode, SignupCodeAdmin)
