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
from account.models import EmailConfirmation, PasswordReset, SignupCode
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
    redirect_field_name = 'next'
    form_class = SignupForm

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

    def get_redirect_field_name(self):
        return self.redirect_field_name

    def get_context_data(self, **kwargs):
        ctx = kwargs
        redirect_field_name = self.get_redirect_field_name()
        ctx.update({
            'redirect_field_name': redirect_field_name,
            'redirect_field_value': self.request.REQUEST.get(redirect_field_name),
        })
        return ctx

    def form_invalid(self, form):
        return JsonResponse(status=0, msg=','.join(form.errors.popitem()[1]))

    def form_valid(self, form):
        # create or update user
        self.created_user = self.create_user(form, commit=False)
        self.after_signup(form)

        response_kwargs = {
            'request': self.request,
            'template': self.template_name_email_confirmation_sent,
            'context': {
                'email': self.created_user.email,
                'need_confirm': settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL
            }
        }
        html = self.response_class(**response_kwargs)
        html.render()
        return JsonResponse(status=1, data={'html': html.content})

    def create_user(self, form, commit=True, **kwargs):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = User()
            user.username = email
            user.email = email

        user.set_password(User.objects.make_random_password(getattr(settings, 'ACCOUNT_RANDOM_PASSWD_LENGTH', 10)))
        user.save()

        return user

    def after_signup(self, form):
        if self.signup_code:
            self.signup_code.use(self.created_user)
        user_signed_up.send(sender=SignupForm, user=self.created_user)

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
                return settings.ACCOUNT_OPEN_SIGNUP
            else:
                return True
        else:
            return settings.ACCOUNT_OPEN_SIGNUP

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
    template_name_failed = 'account/email_unconfirmed.html'
    act = 'change_status'

    def get(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        if confirmation.email_address.verified:
            context = {'already_verified': True}
        else:
            if confirmation.confirm():
                # self.after_confirmation(confirmation)
                self.template_name = self.template_name
            else:
                self.template_name = self.template_name_failed
            context = {}
        return self.render_to_response(self.get_context_data(**context))

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
        pass
        #handle_event.send(sender=profile, verb=Event.SYS_SIGNUP)

        #user.backend = settings.AUTHENTICATION_BACKENDS
        #auth.login(self.request, user)


class ResetPassword(FormView):
    template_name = 'account/reset_pwd.html'
    template_name_sent = 'account/reset_pwd_confirm.html'
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
            return JsonResponse(status=0, msg=','.join(form.errors.popitem()[1]))
        response_kwargs = {
            'request': self.request,
            'template': self.template_name,
            'context': self.get_context_data(form=form)
        }
        return self.response_class(**response_kwargs)

    def form_valid(self, form):
        PasswordReset.create(form.user)

        response_kwargs = {
            'request': self.request,
            'template': self.template_name_sent,
            'context': {
                'email': form.user.email,
            }
        }
        html = self.response_class(**response_kwargs)
        html.render()
        return JsonResponse(status=1, data={'html': html.content})


class ResetPasswordToken(FormView):
    template_name = 'account/reset_pwd_token.html'
    template_name_fail = 'account/reset_pwd_failed.html'
    template_name_done = 'account/reset_pwd_done.html'
    form_class = PasswordResetTokenForm
    token_generator = default_token_generator
    redirect_field_name = 'next'
    act = 'change_password'

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

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(status=0,
                                msg=','.join(form.errors.popitem()[1]))
        return super(ResetPasswordToken, self).form_invalid(form)

    def form_valid(self, form):
        user = self.get_user()
        self.change_password(user, form)
        self.after_change_password(user)

        response_kwargs = {
            'request': self.request,
            'template': self.template_name_done,
        }
        html = self.response_class(**response_kwargs)
        html.render()
        return JsonResponse(status=1, data={'html': html.content})

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
    template_name = 'account/change_pwd.html'
    template_name_done = 'account/change_pwd_done.html'
    form_class = ChangePasswordForm
    redirect_field_name = 'next'
    act = 'change_password'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return HttpResponseForbidden()
        return super(ChangePassword, self).dispatch(request, *args, **kwargs)

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
        signals.password_changed.send(sender=ChangePassword, user=self.request.user)
        auth.logout(self.request)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(status=0, msg=','.join(form.errors.popitem()[1]))
        return super(ChangePassword, self).form_invalid(form)

    def form_valid(self, form):
        self.change_password(form)
        self.after_change_password()

        response_kwargs = {
            'request': self.request,
            'template': self.template_name_done
        }
        html = self.response_class(**response_kwargs)
        html.render()
        return JsonResponse(status=1, data={'html': html.content})
