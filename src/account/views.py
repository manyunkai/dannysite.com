# -*-coding:utf-8 -*-

import datetime

from django.conf import settings
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import base36_to_int
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages, auth
from django.contrib.auth.tokens import default_token_generator
from django.views.generic.edit import FormView
from django.views.generic.base import View, TemplateResponseMixin

from core.http import JsonResponse
from account import signals
from account.models import EmailAddress, EmailConfirmation, PasswordReset,\
    SignupCode
from account.utils import default_redirect
from account.forms import ChangePasswordForm, PasswordResetForm,\
    PasswordResetTokenForm, LoginForm, SignupForm
from account.signals import user_signed_up
from user.models import User


class NoActionSupplied(BaseException):
    pass


class Login(FormView):
    template_name = 'account/login.html'
    form_class = LoginForm
    form_kwargs = {}
    redirect_field_name = 'next'

    def get(self, *args, **kwargs):
        self.request.session['redirect_to'] = self.request.REQUEST.get('next', '')\
                                              or self.request.META.get('HTTP_REFERER', '/')
        if self.request.user.is_authenticated():
            return redirect(self.get_success_url())
        return super(Login, self).get(*args, **kwargs)

    def get_template_names(self):
        return [self.template_name]

    def get_context_data(self, **kwargs):
        ctx = kwargs
        redirect_field_name = self.get_redirect_field_name()
        ctx.update({
            'redirect_field_name': redirect_field_name,
            'redirect_field_value': self.request.REQUEST.get(redirect_field_name),
        })
        return ctx

    def get_form_kwargs(self):
        kwargs = super(Login, self).get_form_kwargs()
        kwargs.update(self.form_kwargs)
        return kwargs

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(status=0, msg=','.join(form.errors.popitem()[1]))
        return super(Login, self).form_invalid(form)

    def form_valid(self, form):
        self.login_user(form)
        self.after_login(form)

        if self.request.is_ajax():
            return JsonResponse(status=1, data={'redirect': self.get_success_url()})
        return redirect(self.get_success_url())

    def after_login(self, form):
        pass

    def get_success_url(self, fallback_url=None, **kwargs):
        if fallback_url is None:
            fallback_url = settings.ACCOUNT_LOGIN_REDIRECT_URL
        kwargs.setdefault('redirect_field_name', self.get_redirect_field_name())
        return default_redirect(self.request, fallback_url, **kwargs)

    def get_redirect_field_name(self):
        return self.redirect_field_name

    def login_user(self, form):
        auth.login(self.request, form.user)
        form.user.reset_login_attempted_count()
        expiry = settings.ACCOUNT_REMEMBER_ME_EXPIRY if form.cleaned_data.get('remember') else 0
        self.request.session.set_expiry(expiry)


class Signup(FormView):
    template_name = 'account/signup.html'
    template_name_email_confirmation_sent = 'account/signup_done.html'
    template_name_signup_closed = 'account/signup_closed.html'
    form_class = SignupForm
    form_kwargs = {}
    redirect_field_name = 'next'
    messages = {
        'email_confirmation_sent': {
            'level': messages.INFO,
            'text': _('Confirmation email sent to {email}.')
        },
        'invalid_signup_code': {
            'level': messages.WARNING,
            'text': _('The code {code} is invalid.')
        },
        'signup_closed': {
            'level': messages.WARNING,
            'text': _('Signup closed')
        }
    }

    def __init__(self, *args, **kwargs):
        self.created_user = None
        kwargs['signup_code'] = None
        super(Signup, self).__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect(default_redirect(self.request, settings.ACCOUNT_LOGIN_REDIRECT_URL))
        if not self.is_open():
            return self.closed()
        return super(Signup, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if not self.is_open():
            return self.closed()
        return super(Signup, self).post(*args, **kwargs)

    def get_template_names(self):
        return [self.template_name]

    def get_context_data(self, **kwargs):
        ctx = kwargs
        redirect_field_name = self.get_redirect_field_name()
        ctx.update({
            'redirect_field_name': redirect_field_name,
            'redirect_field_value': self.request.REQUEST.get(redirect_field_name),
        })
        return ctx

    def get_form_kwargs(self):
        kwargs = super(Signup, self).get_form_kwargs()
        kwargs.update(self.form_kwargs)
        return kwargs

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(status=0, msg=','.join(form.errors.popitem()[1]))
        return super(Signup, self).form_invalid(form)

    def form_valid(self, form):
        # create or update user
        self.created_user = self.create_user(form, commit=False)
        # prevent User post_save signal from creating an Account instance
        # we want to handle that ourself.
        # self.created_user._disable_account_creation = True
        # self.created_user.save()

        email_address = self.create_email_address(form)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED and not email_address.verified:
            self.created_user.is_active = False
            self.created_user.save()

        # self.create_account(form)
        self.after_signup(form)

        if settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL and not email_address.verified:
            self.send_confirmation_email(email_address)
            return self.email_confirmation_required_response()
        else:
            show_message = [
                settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL,
                self.messages.get('email_confirmation_sent'),
                not email_address.verified
            ]
            if all(show_message):
                messages.add_message(
                    self.request,
                    self.messages['email_confirmation_sent']['level'],
                    self.messages['email_confirmation_sent']['text'].format(**{
                        'email': form.cleaned_data['email']
                    })
                )
            self.login_user()

        #return redirect(self.get_success_url())
        self.template_name = self.template_name_email_confirmation_sent
        return self.render_to_response(self.get_context_data(email=email_address.email))

    def get_success_url(self, fallback_url=None, **kwargs):
        if fallback_url is None:
            fallback_url = settings.ACCOUNT_SIGNUP_REDIRECT_URL
        kwargs.setdefault('redirect_field_name', self.get_redirect_field_name())
        return default_redirect(self.request, fallback_url, **kwargs)

    def get_redirect_field_name(self):
        return self.redirect_field_name

    def create_user(self, form, commit=True, **kwargs):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = User()
            user.username = email
            user.email = email

        user.set_password(User.objects.make_random_password())
        user.save()

        return user

    def create_email_address(self, form, **kwargs):
        kwargs.setdefault('primary', True)
        kwargs.setdefault('verified', False)
        if self.signup_code:
            self.signup_code.use(self.created_user)
            kwargs['verified'] = self.signup_code.email and self.created_user.email == self.signup_code.email
        return EmailAddress.objects.add_email(self.created_user, self.created_user.email)

    def send_confirmation_email(self, email_address):
        EmailConfirmation.create(email_address)

    def after_signup(self, form):
        """ mainly create profile entity """
        user_signed_up.send(sender=SignupForm, user=self.created_user, form=form)

    def login_user(self):
        # set backend on User object to bypass needing to call auth.authenticate
        #self.created_user.backend = 'account.auth_backends.AuthenticationBackend'
        auth.login(self.request, self.created_user)
        self.request.session.set_expiry(0)

    def is_open(self):
        code = self.request.REQUEST.get('code')
        if code:
            try:
                self.signup_code = SignupCode.check(code)
            except SignupCode.InvalidCode:
                if self.messages.get('invalid_signup_code'):
                    messages.add_message(
                        self.request,
                        self.messages['invalid_signup_code']['level'],
                        self.messages['invalid_signup_code']['text'].format(**{
                            'code': code
                        })
                    )
                return settings.ACCOUNT_OPEN_SIGNUP
            else:
                return True
        else:
            return settings.ACCOUNT_OPEN_SIGNUP

    def email_confirmation_required_response(self):
        if self.request.is_ajax():
            #template_name = self.template_name_email_confirmation_sent_ajax
            return JsonResponse(status=1,
                                msg=u'注册成功！请转至注册邮箱中查收激活邮件。')
        else:
            template_name = self.template_name_email_confirmation_sent
        response_kwargs = {
            'request': self.request,
            'template': template_name,
            'context': {
                'email': self.created_user.email,
                'success_url': self.get_success_url(),
            }
        }
        return self.response_class(**response_kwargs)

    def closed(self):
        # TODO ...
        return HttpResponseForbidden()

        if self.request.is_ajax():
            template_name = self.template_name_signup_closed_ajax
        else:
            template_name = self.template_name_signup_closed
        response_kwargs = {
            'request': self.request,
            'template': template_name,
        }
        return self.response_class(**response_kwargs)


class Logout(View):
    redirect_field_name = 'next'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            auth.logout(self.request)

        self.request.session['redirect_to'] = self.request.REQUEST.get('next', '')\
                                              or self.request.META.get('HTTP_REFERER', '/')

        if self.request.is_ajax():
            return JsonResponse(status=1,
                                data={'redirect': self.get_redirect_url()})
        return redirect(self.get_redirect_url())

    def get_redirect_field_name(self):
        return self.redirect_field_name

    def get_redirect_url(self, fallback_url=None, **kwargs):
        if fallback_url is None:
            fallback_url = settings.ACCOUNT_LOGOUT_REDIRECT_URL
        kwargs.setdefault('redirect_field_name', self.get_redirect_field_name())
        return default_redirect(self.request, fallback_url, **kwargs)


class ConfirmEmail(TemplateResponseMixin, View):
    template_name = 'account/email_confirmed.html'
    act = 'change_status'
    messages = {
        'email_confirmed': {
            'level': messages.SUCCESS,
            'text': _('You have confirmed {email}.')
        }
    }

    def get(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm()

        self.after_confirmation(confirmation)

        if self.messages.get('email_confirmed'):
            messages.add_message(
                self.request,
                self.messages['email_confirmed']['level'],
                self.messages['email_confirmed']['text'].format(**{
                    'email': confirmation.email_address.email
                })
            )

        ctx = self.get_context_data()
        ctx['form'] = LoginForm()
        return self.render_to_response(ctx)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(confirmation_key=self.kwargs['key'].lower())
        except EmailConfirmation.DoesNotExist:
            raise Http404()

    def get_queryset(self):
        qs = EmailConfirmation.objects.all()
        qs = qs.select_related('email_address__user')
        return qs

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx['confirmation'] = self.object
        return ctx

    def after_confirmation(self, confirmation):
        user = confirmation.email_address.user
        profile = user.activate()

        #handle_event.send(sender=profile, verb=Event.SYS_SIGNUP)

        #user.backend = settings.AUTHENTICATION_BACKENDS
        #auth.login(self.request, user)


class ResetPassword(FormView):
    template_name = 'account/password_reset_email.html'
    template_name_sent = 'account/password_reset_email_sent.html'
    template_name_sent_ajax = 'account/password_reset_sent.html'
    form_class = PasswordResetForm

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect('profile_get_options_page')
        return super(ResetPassword, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = kwargs
        if self.request.method == 'POST' and 'resend' in self.request.POST:
            context['resend'] = True
        return context

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(status=0,
                                msg=','.join(form.errors.popitem()[1]))
        response_kwargs = {
            'request': self.request,
            'template': self.template_name,
            'context': self.get_context_data(form=form)
        }
        return self.response_class(**response_kwargs)

    def form_valid(self, form):
        PasswordReset.create(form.user)

        if self.request.is_ajax():
            #t = get_template(self.template_name_sent_ajax)
            #t.render(RequestContext(self.request,
            #                        self.get_context_data(form=form)))
            return JsonResponse(status=1, msg=u'重置密码邮件已发送至该邮箱。')

        response_kwargs = {
            'request': self.request,
            'template': self.template_name_sent,
            'context': self.get_context_data(form=form)
        }

        self.template_name = self.template_name_sent
        return self.response_class(**response_kwargs)


class ResetPasswordToken(FormView):
    template_name = 'account/password_reset_token.html'
    template_name_fail = 'account/password_reset_failed.html'
    template_name_done = 'account/password_reset_done.html'
    form_class = PasswordResetTokenForm
    token_generator = default_token_generator
    redirect_field_name = 'next'
    act = 'change_password'
    messages = {
        'password_changed': {
            'level': messages.SUCCESS,
            'text': _('Password successfully changed.')
        },
    }

    def get(self, request, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        ctx = self.get_context_data(form=form)
        if not PasswordReset.objects.check_token(self.get_user(),
                                                 self.kwargs['token']):
            return self.token_fail()
        return self.render_to_response(ctx)

    def get_context_data(self, **kwargs):
        ctx = kwargs
        redirect_field_name = self.get_redirect_field_name()
        ctx.update({
            'uidb36': self.kwargs['uidb36'],
            'token': self.kwargs['token'],
            'redirect_field_name': redirect_field_name,
            'redirect_field_value': self.request.REQUEST.get(redirect_field_name),
        })
        return ctx

    def change_password(self, user, form):
        user.set_password(form.cleaned_data['password'])
        user.reset_login_attempted_count()
        user.save()

    def after_change_password(self, user):
        signals.password_changed.send(sender=ResetPasswordToken, user=user)
        if self.messages.get('password_changed'):
            messages.add_message(
                self.request,
                self.messages['password_changed']['level'],
                self.messages['password_changed']['text']
            )

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(status=0,
                                msg=','.join(form.errors.popitem()[1]))
        return super(ResetPasswordToken, self).form_invalid(form)

    def form_valid(self, form):
        user = self.get_user()
        self.change_password(user, form)
        self.after_change_password(user)
        if self.request.is_ajax():
            return JsonResponse(status=1, msg='密码修改成功')
        self.template_name = self.template_name_done
        return self.render_to_response({'form': LoginForm})

    def get_redirect_field_name(self):
        return self.redirect_field_name

    def get_success_url(self, fallback_url=None, **kwargs):
        if fallback_url is None:
            fallback_url = settings.ACCOUNT_PASSWORD_RESET_REDIRECT_URL
        kwargs.setdefault('redirect_field_name', self.get_redirect_field_name())
        return default_redirect(self.request, fallback_url, **kwargs)

    def get_user(self):
        try:
            uid_int = base36_to_int(self.kwargs['uidb36'])
        except ValueError:
            raise Http404()
        return get_object_or_404(User, id=uid_int)

    def token_fail(self):
        response_kwargs = {
            'request': self.request,
            'template': self.template_name_fail,
            'context': self.get_context_data(form=PasswordResetForm()),
        }
        return self.response_class(**response_kwargs)


class ChangePassword(FormView):
    template_name = 'account/password_change.html'
    template_name_done = 'account/password_change_done.html'
    form_class = ChangePasswordForm
    redirect_field_name = 'next'
    act = 'change_password'
    messages = {
        'password_changed': {
            'level': messages.SUCCESS,
            'text': _('Password successfully changed.')
        }
    }

    def get(self, *args, **kwargs):
        return redirect('profile_get_options_page')

    def post(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return HttpResponseForbidden()
        return super(ChangePassword, self).post(*args, **kwargs)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {'user': self.request.user, 'initial': self.get_initial()}
        if self.request.method in ['POST', 'PUT']:
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def change_password(self, form):
        user = self.request.user
        user.set_password(form.cleaned_data['password_new'])
        user.save()

    def after_change_password(self):
        user = self.request.user
        user.extenduser.last_pwdchanged = datetime.datetime.now()
        user.extenduser.save()

        signals.password_changed.send(sender=ChangePassword, user=user)
        if settings.ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE:
            self.send_email(user)
        if self.messages.get('password_changed'):
            messages.add_message(
                self.request,
                self.messages['password_changed']['level'],
                self.messages['password_changed']['text']
            )

        auth.logout(self.request)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(status=0,
                                msg=','.join(form.errors.popitem()[1]))
        return super(ChangePassword, self).form_invalid(form)

    def form_valid(self, form):
        self.change_password(form)
        self.after_change_password()
        if self.request.is_ajax():
            return JsonResponse(status=1, msg=u'密码修改成功')
        self.template_name = self.template_name_done
        return self.render_to_response({})
