# -*-coding:utf-8 -*-

import datetime
import operator
import uuid

from django.utils.translation import get_language_from_request, ugettext_lazy as _
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db import models, IntegrityError
from django.utils import timezone
from django.db.models.query_utils import Q

from account.utils import random_token
from account import signals
from account.signals import signup_code_used
from user.models import User


class AnonymousAccount(object):
    def __init__(self, request=None):
        self.user = AnonymousUser()
        self.timezone = settings.TIME_ZONE
        if request is not None:
            self.language = get_language_from_request(request)
        else:
            self.language = settings.LANGUAGE_CODE

    def __unicode__(self):
        return "AnonymousAccount"


class PasswordResetManager(models.Manager):
    def make_token(self, user):
        return default_token_generator.make_token(user)

    def check_token(self, user, token):
        return default_token_generator.check_token(user, token)

    def save_presend_email(self, obj, email_address):
        from mail.signals import add_mail
        add_mail.send(sender=self, target=obj, email=email_address)


class PasswordReset(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"))
    temp_key = models.CharField(_("temp_key"), max_length=100)
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)
    reset = models.BooleanField(_("reset yet?"), default=False)

    objects = PasswordResetManager()

    class Meta:
        db_table = 'acct_password_reset'
        verbose_name = 'PasswordReset'

    def __unicode__(self):
        return "%s (key=%s, reset=%r)" % (self.user.username,
                                          self.temp_key,
                                          self.reset)

    @classmethod
    def create(cls, user):
        key = cls._default_manager.make_token(user)

        cls._default_manager.filter(user=user).delete()
        obj = cls._default_manager.create(user=user, temp_key=key)

        cls._default_manager.save_presend_email(obj, user.email)

        return obj


class SignupCode(models.Model):

    class AlreadyExists(Exception):
        pass

    class InvalidCode(Exception):
        pass

    code = models.CharField(u'邀请码', max_length=64, unique=True)
    max_uses = models.PositiveIntegerField(u'可用次数', default=1)
    expiry = models.DateTimeField(u'过期时间', null=True, blank=True)
    inviter = models.ForeignKey(User, verbose_name=u'邀请人', null=True, blank=True)
    email = models.EmailField(u'受邀者邮箱地址', blank=True)
    notes = models.TextField(u'留言', blank=True)
    sent = models.DateTimeField(u'邮件发送状态', null=True, blank=True)
    created = models.DateTimeField(u'创建时间', default=timezone.now, editable=False)
    use_count = models.PositiveIntegerField(u'已用次数', editable=False, default=0)

    class Meta:
        db_table = 'acct_signup_code'
        verbose_name = u'注册邀请码'
        verbose_name_plural = u'注册邀请码'

    def __unicode__(self):
        if self.email:
            return '{0} [{1}]'.format(self.email, self.code)
        else:
            return self.code

    def generate_code(self):
        self.code = str(uuid.uuid1()).replace('-', '')

    @classmethod
    def exists(cls, code=None, email=None):
        checks = []
        if code:
            checks.append(Q(code=code))
        if email:
            checks.append(Q(email=code))

        # reduce(function, iterable[, initializer]): Apply function of
        # two arguments cumulatively to the items of iterable,
        # from left to right, so as to reduce the iterable to a single value.
        return cls._default_manager.filter(reduce(operator.or_, checks)).exists()

    @classmethod
    def create(cls, **kwargs):
        email, code = kwargs.get('email'), kwargs.get('code')
        if kwargs.get('check_exists', True) and cls.exists(code=code, email=email):
            raise cls.AlreadyExists()
        expiry = timezone.now() + datetime.timedelta(hours=kwargs.get('expiry', 24))
        if not code:
            code = random_token([email]) if email else random_token()
        params = {
            'code': code,
            'max_uses': kwargs.get('max_uses', 0),
            'expiry': expiry,
            'inviter': kwargs.get('inviter'),
            'notes': kwargs.get('notes', '')
        }
        if email:
            params['email'] = email
        return cls(**params)

    @classmethod
    def check(cls, code):
        try:
            signup_code = cls._default_manager.get(code=code)
        except cls.DoesNotExist:
            raise cls.InvalidCode()
        else:
            if signup_code.max_uses and signup_code.max_uses <= signup_code.use_count:
                raise cls.InvalidCode()
            else:
                if signup_code.expiry and timezone.now() > signup_code.expiry:
                    raise cls.InvalidCode()
                else:
                    return signup_code

    def calculate_use_count(self):
        self.use_count = self.signupcoderesult_set.count()
        self.save()

    def use(self, user):
        """
        Add a SignupCode result attached to the given user.
        """
        result = SignupCodeResult()
        result.signup_code = self
        result.user = user
        result.save()
        signup_code_used.send(sender=result.__class__, signup_code_result=result)

#     def send(self, **kwargs):
#         protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
#         current_site = kwargs["site"] if "site" in kwargs else Site.objects.get_current()
#         signup_url = "{0}://{1}{2}?{3}".format(
#             protocol,
#             current_site.domain,
#             reverse("account_signup"),
#             urllib.urlencode({"code": self.code})
#         )
#         ctx = {
#             "signup_code": self,
#             "current_site": current_site,
#             "signup_url": signup_url,
#         }
#         subject = render_to_string("account/email/invite_user_subject.txt", ctx)
#         message = render_to_string("account/email/invite_user.txt", ctx)
#         send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])
#         self.sent = timezone.now()
#         self.save()
#         signup_code_sent.send(sender=SignupCode, signup_code=self)


class SignupCodeResult(models.Model):

    signup_code = models.ForeignKey(SignupCode)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'acct_signup_code_result'
        verbose_name = u'邀请注册用户'

    def save(self, **kwargs):
        super(SignupCodeResult, self).save(**kwargs)
        self.signup_code.calculate_use_count()


# Following code about email.
class EmailAddressManager(models.Manager):
    def add_email(self, user, email):
        try:
            email_address = self.create_or_get_email(user=user, email=email)
            return email_address
        except IntegrityError:
            return None

    # To replace the self.create(user=user, email=email) method
    def create_or_get_email(self, user, email):
        try:
            emailAddress = EmailAddress.objects.get(user=user, email=email)
            return emailAddress
        except EmailAddress.DoesNotExist:
            return self.create(user=user, email=email)

    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except EmailAddress.DoesNotExist:
            return None

    def get_users_for(self, email):
        """
        returns a list of users with the given email.
        """
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [address.user for address in EmailAddress.objects.filter(
            verified=True, email=email)]


class EmailAddress(models.Model):
    user = models.ForeignKey(User, related_name=u'user', verbose_name=u'用户')
    email = models.EmailField(u'邮箱')
    verified = models.BooleanField(u'验证状态', default=False)
    primary = models.BooleanField(u'主邮箱', default=False)

    objects = EmailAddressManager()

    def __unicode__(self):
        return u'%s (%s)' % (self.email, self.user)

    def set_as_primary(self, conditional=False):
        old_primary = EmailAddress.objects.get_primary(self.user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        self.user.email = self.email
        self.user.save()
        return True

    class Meta:
        db_table = 'acct_email_address'
        verbose_name = u'邮箱绑定'
        verbose_name_plural = u'邮箱绑定'
        unique_together = (
            ('user', 'email'),
        )


class EmailConfirmationManager(models.Manager):
    def save_presend_email(self, obj, email_address):
        from mail.signals import add_mail
        add_mail.send(sender=self, target=obj, email=email_address)

    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                confirmation.delete()


class EmailConfirmation(models.Model):
    email_address = models.ForeignKey(EmailAddress)
    created = models.DateTimeField(default=timezone.now())
    sent = models.DateTimeField(auto_now_add=True)
    confirmation_key = models.CharField(max_length=64)

    objects = EmailConfirmationManager()

    class Meta:
        db_table = 'acct_email_confirmation'
        verbose_name = _('email confirmation')
        verbose_name_plural = _('email confirmations')

    def __unicode__(self):
        return 'confirmation for {0}'.format(self.email_address)

    @classmethod
    def create(cls, email_address):
        key = random_token([email_address.email])

        cls._default_manager.filter(email_address=email_address).delete()
        obj = cls._default_manager.create(email_address=email_address,
                                          confirmation_key=key)

        cls._default_manager.save_presend_email(obj, email_address.email)

        return obj

    def key_expired(self):
        expiration_date = self.sent + datetime.timedelta(days=settings.ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS)
        return expiration_date <= timezone.now()
    key_expired.boolean = True

    def confirm(self):
        if not self.key_expired() and not self.email_address.verified:
            email_address = self.email_address
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()
            signals.email_confirmed.send(sender=self.__class__, email_address=email_address)
            return email_address
