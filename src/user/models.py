# -*-coding:utf-8 -*-
'''
Created on 2013-10-15

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group,\
    Permission, _user_get_all_permissions, _user_has_perm,\
    _user_has_module_perms
from django.utils import timezone
from django.contrib import auth
from django.utils.http import urlquote
from django.core.mail import send_mail
from django.utils.timezone import utc
from django.conf import settings


class UserManager(BaseUserManager):

    def create_user(self, username, email=None, password=None, **extra_fields):
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = UserManager.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        u = self.create_user(username, email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class PermissionsMixin(models.Model):
    is_superuser = models.BooleanField(u'超级管理员', default=False)
    groups = models.ManyToManyField(Group, verbose_name=u'用户组', blank=True)
    user_permissions = models.ManyToManyField(Permission,
                                              verbose_name=u'用户权限',
                                              blank=True)

    class Meta:
        abstract = True

    def get_group_permissions(self, obj=None):
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                if obj is not None:
                    permissions.update(backend.get_group_permissions(self,
                                                                     obj))
                else:
                    permissions.update(backend.get_group_permissions(self))
        return permissions

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj)

    def has_perm(self, perm, obj=None):
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(u'用户名', max_length=75, unique=True, db_index=True)
    email = models.EmailField(u'邮箱', blank=True)
    is_staff = models.BooleanField(u'职员身份', default=False)
    is_active = models.BooleanField(u'激活状态', default=False)
    date_joined = models.DateTimeField(u'注册时间', default=timezone.now)

    login_attempted = models.IntegerField(u'登录失败计次', default=0)
    updated = models.DateTimeField(u'上次登录尝试', auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    backend = 'user.backends.AuthenticationBackend'

    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = u'用户'
        swappable = 'AUTH_USER_MODEL'

    def is_locked(self):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        if self.login_attempted >= settings.ACCOUNT_LOCK_BY_ATTEMPTED_COUNT:
            if (now - self.updated).seconds < settings.ACCOUNT_LOCK_TIME:
                return True
            else:
                self.login_attempted = 0
                self.save()
        return False

    def incr_login_attempted_count(self):
        self.login_attempted += 1
        self.save()

    def reset_login_attempted_count(self):
        self.login_attempted = 0
        self.save()

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def activate(self):
        self.is_active = True
        self.save()

        return Profile.objects.get_or_create(user=self)


USER_SEX_CHOICES = (
    ('M', u'男'),
    ('F', u'女'),
)


class Profile(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(u'头衔', max_length=20, blank=True)
    nickname = models.CharField(u'昵称', max_length=30, blank=True)
    sex = models.CharField(u'性别', max_length=1, choices=USER_SEX_CHOICES,
                              blank=True, null=True)
    location = models.CharField(u'所在地', max_length=50, blank=True)
    qq = models.CharField(u'QQ', max_length=15, blank=True)
    msn = models.EmailField(u'MSN', blank=True)
    website = models.URLField(u'个性主页', blank=True)
    website_auth = models.BooleanField(u'个性主页认证状态', default=True)
    avatar = models.CharField(u'个性头像', max_length=50, blank=True)
    signature = models.CharField(u'个性签名', max_length=200, blank=True)

    def __unicode__(self):
        return self.user.get_short_name()

    class Meta:
        verbose_name = u'用户信息'
        verbose_name_plural = u'用户信息'
