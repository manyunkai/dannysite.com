# -*-coding:utf-8 -*-
'''
Created on 2013-10-15

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.contrib.auth.backends import ModelBackend

from user.models import User


class AuthenticationBackend(ModelBackend):

    def authenticate(self, **credentials):
        lookup_params = {}

        field, identity = "email__iexact", credentials.get("email", None)
        if not identity:
            #this if branch just for admin login
            field, identity = "username__iexact", credentials.get("username", None)

        lookup_params[field] = identity
        try:
            user = User.objects.get(**lookup_params)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(credentials.get("password", '')):
                return user
            user.incr_login_attempted_count()


EmailModelBackend = AuthenticationBackend
