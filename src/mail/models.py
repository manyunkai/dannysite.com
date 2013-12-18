# -*-coding:utf-8 -*-
'''
Created on 2013-10-15

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

import datetime
from hashlib import md5

from django.db import models, transaction
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.template.loader import render_to_string, get_template
from django.template.context import Context
from django.core.urlresolvers import reverse
from django.core.mail.message import EmailMultiAlternatives
from django.utils.http import int_to_base36
from django.utils.timezone import utc

from user.models import User
from account.models import EmailAddress
from mail.signals import add_mail
from common.log_utils import set_log


class EmailSentCountManager(models.Manager):
    def is_max_email_sent_count(self, email_address, send_type):
        try:
            email = self.get(email_address=email_address, send_type=send_type)
        except:
            email = self.create(email_address=email_address, send_type=send_type)
        else:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            if (now - email.update_time).seconds > settings.EMAIL_COUNTER_RESET_INTERVAL:
                email.count = 0

        if email.count >= settings.MAX_EMAIL_SENT_COUNT_PERDAY:
            return True

        email.count += 1
        email.save()

        return False


class EmailSentCount(models.Model):
    """
    Count the email sent times
    """

    email_address = models.EmailField(u'邮箱')
    send_type = models.CharField(u'邮件类型', max_length=10)
    count = models.IntegerField(u'周期累计', default=0)
    update_time = models.DateTimeField(u'最后更新', auto_now=True)

    objects = EmailSentCountManager()

    class Meta:
        db_table = 'mail_sent_count'
        verbose_name = u'邮件发送统计'
        verbose_name_plural = u'邮件发送统计'


@transaction.commit_manually
def flush_transaction():
    transaction.commit()


class EailWaitingManager(models.Manager):
    def get_unconfirmed_email_ids(self):
        flush_transaction()
        return EmailWaiting.objects.values_list('id', flat=True).filter(is_sent=False)

    def create(self, obj, email_addresses, site=None):
        if type(email_addresses) == list:
            email_addresses = ','.join(email_addresses)
        ctype = ContentType.objects.get_for_model(obj)

        return super(EailWaitingManager, self).create(
                    related_object_content_type=ctype,
                    related_object_object_id=obj.pk,
                    email_addresses=email_addresses,
                    from_site=site, is_sent=False)


class EmailWaiting(models.Model):
    """
    Saving emails waiting to be sent.
    """

    # Related Obj
    related_object_content_type = models.ForeignKey(ContentType,
                                                    related_name='related_obj')
    related_object_object_id = models.CharField(max_length=255)
    related_object = generic.GenericForeignKey('related_object_content_type',
                                               'related_object_object_id')

    email_addresses = models.CharField(u'投递邮箱', max_length=1000)

    from_site = models.ForeignKey(Site, null=True, blank=True)

    sn = models.CharField(max_length=32)
    created = models.DateTimeField(u'创建时间', auto_now=True)
    is_sent = models.BooleanField(u'投递状态', default=False)

    objects = EailWaitingManager()

    class Meta:
        db_table = 'mail_waiting'
        verbose_name = u'邮件投递'
        verbose_name_plural = u'邮件投递'

    def _gen_sn(self):
        s = '&'.join([str(self.related_object_content_type),
                      str(self.related_object_object_id),
                      self.email_addresses,
                      str(self.created)])
        return md5(s).hexdigest()

    def save(self, *args, **kwargs):
        if not self.id:
            self.sn = self._gen_sn()
        super(EmailWaiting, self).save(*args, **kwargs)

    def mark_sent(self):
        self.is_sent = True
        self.save()

    def get_site(self):
        return self.from_site if self.from_site else Site.objects.get_current()

    def render(self, context, domain,
               txt_template_name=None, html_template_name=None):
        context['domain'] = domain
        context['STATIC_URL'] = settings.STATIC_URL

        text = render_to_string(txt_template_name, context) if txt_template_name else ''

        if html_template_name:
            t = get_template(html_template_name)
            html = t.render(Context(context))
        else:
            html = ''

        return text, html

    def _pack_passwordreset(self, email):
        user = User.objects.get(email__iexact=email)
        domain = unicode(self.get_site().domain)
        subject = settings.PASSWD_RESET_SUBJECT

        context = {
            'user': user,
            'protocol': getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http'),
            'uid': int_to_base36(user.id),
            'temp_key': self.related_object.temp_key,
        }

        text, html = self.render(context, domain,
                                 settings.PWD_RESET_MSG,
                                 settings.PWD_RESET_HTML)

        return subject, text, html

    def _pack_email_confirmation(self, email):
        confirmation_key = self.related_object.confirmation_key
        current_site = self.get_site()

        activate_url = u'%s://%s%s' % (
            getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http'),
            unicode(unicode(current_site.domain)),
            reverse('acct_confirm_email', args=[confirmation_key])
        )

        subject = ''.join(settings.EMAIL_CONFIRMATION_SUBJECT.splitlines())

        passwd = User.objects.make_random_password()
        user = EmailAddress.objects.get(email=email).user
        user.set_password(passwd)
        user.save()

        context = {'username': user.username,
                   'password': passwd,
                   'activate_url': activate_url}

        text, html = self.render(context, unicode(current_site.domain),
                                 settings.EMAIL_CONFIRMATION_MESSAGE,
                                 settings.EMAIL_CONFIRMATION_HTML)

        return subject, text, html

    def _pack_d_comment(self, email):
        context = {
            'comment': self.related_object,
            'sn': self.sn
        }
        print context, self, self.sn, self.sn
        current_site = self.get_site()
        subject = settings.EMAIL_CMT_REPLY_SUBJECT

        text, html = self.render(context, unicode(current_site.domain),
                                 settings.EMAIL_CMT_REPLY_MESSAGE,
                                 settings.EMAIL_CMT_REPLY_HTML)

        return subject, text, html

    def send(self):
        try:
            model_name = ContentType.objects.get_for_model(self.related_object)
        except:
            set_log('info', 'The related object has been deleted when trying to send mail to {0}'.format(self.email_addresses))
            self.is_sent = True
            return True

        emails = self.email_addresses.split(',')
        sended = []

        for email in emails:
            subject, text, html = getattr(self, '_'.join(['_pack', model_name.name.lower().replace(' ', '_')]))(email)

            message = EmailMultiAlternatives(subject, text,
                                             settings.DEFAULT_FROM_EMAIL,
                                             [email])
            if html:
                message.attach_alternative(html, "text/html")

            try:
                message.send()
            except Exception, e:
                set_log('error', 'Mail Server eror: ' + str(e))
                self.email_addresses = ','.join(set(emails) - set(sended))
                return False
            else:
                sended.append(email)

            self.mark_sent()

        return True


def mail_adder(verb=None, **kwargs):
    """
    Handler function to add EmailWaiting instance and
    push it to mail sending pool upon action signal call.
    """

    obj = EmailWaiting.objects.create(kwargs.get('target'),
                                      kwargs.get('email'),
                                      kwargs.get('site'))

    import redis
    conn = redis.Redis()

    conn.lpush(settings.EMAIL_PRESENDING_POOL, obj.id)

# connect the signal
add_mail.connect(mail_adder, dispatch_uid='mail.models.email_waiting')
