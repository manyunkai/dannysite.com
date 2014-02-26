# -*-coding:utf-8 -*

from django.contrib import auth
from django import forms
from django.utils.translation import ugettext_lazy as _

from account.models import EmailAddress
from account.utils import perform_login
from mail.models import EmailSentCount
from user.models import User


class LoginForm(forms.Form):
    email = forms.EmailField(error_messages={'required': u'请正确填写您的用户名和密码',
                                             'invalid': u'请正确填写您的用户名和密码'})
    password = forms.CharField(widget=forms.PasswordInput(render_value=False),
                               error_messages={'required': u'请正确填写您的用户名和密码'})
    remember = forms.BooleanField(required=False)

    user = None

    def user_credentials(self):
        return {
            'email': self.cleaned_data['email'],
            'password': self.cleaned_data['password']}

    def clean(self):
        if self._errors:
            return

        try:
            user = User.objects.get(email=self.cleaned_data.get('email'), is_active=True)
        except User.DoesNotExist:
            raise forms.ValidationError(u'该账号无效或尚未激活')

        if user.is_locked():
            raise forms.ValidationError(u'您的账户应多次尝试登录失败而被暂时锁定，请稍后再试或联系管理员协助解决')

        if not auth.authenticate(**self.user_credentials()):
            raise forms.ValidationError(u'用户名或密码错误，请重试。如果您多次登录无效，系统可能会暂时锁定您的账户')

        self.user = user
        return self.cleaned_data

    def login(self, request):
        perform_login(request, self.user)

        if self.cleaned_data['remember']:
            request.session.set_expiry(60 * 60 * 24 * 7 * 3)
        else:
            request.session.set_expiry(0)


class SignupForm(forms.Form):
    email = forms.EmailField(error_messages={'required': u'请填写有效的电子邮箱',
                                             'invalid': u'请正确填写您的电子邮箱'})

    email_address = None

    def clean_email(self):
        value = self.cleaned_data.get('email', '').strip().lower()
        if not value:
            raise forms.ValidationError(u"请填写有效的电子邮箱")

        if EmailAddress.objects.filter(user__email__iexact=value, verified=True).exists() or \
                    User.objects.filter(email__iexact=value, is_active=True).exists():
                raise forms.ValidationError(u"该邮箱已被注册")

        if EmailSentCount.objects.is_max_email_sent_count(value, 'activation'):
            raise forms.ValidationError(_(u"该Email已达到今日注册激活次数上限"))
        return value


class PasswordResetForm(forms.Form):

    email = forms.EmailField(label=_('Email'),
                             error_messages={'required': u'请填写注册时的邮箱'})
    user = None

    def clean_email(self):
        value = self.cleaned_data.get("email", '').strip().lower()

        try:
            self.user = User.objects.get(email__iexact=value, is_active=True)
        except:
            raise forms.ValidationError(_(u"该账号尚未激活"))

        # 超级用户和管理员不可使用该方法重置密码
        if self.user.is_superuser or self.user.is_staff or EmailSentCount.objects.is_max_email_sent_count(value, 'password'):
            raise forms.ValidationError(u'该Email已达到今日最大密码重置次数')
        return value


class PasswordResetTokenForm(forms.Form):

    password = forms.CharField(label=u"新密码",
                               widget=forms.PasswordInput(render_value=False),
                               min_length=6,
                               error_messages={'required': '请输入新密码',
                                               'min_length': '密码长度不应小于6位'})
    password_confirm = forms.CharField(label=u"重复密码",
                                       widget=forms.PasswordInput(render_value=False),
                                       required=False)

    def clean_password_confirm(self):
        if not self.cleaned_data.get('password') ==\
                self.cleaned_data.get('password_confirm'):
            raise forms.ValidationError(u'两次输入的密码不匹配')
        return self.cleaned_data["password_confirm"]


class ChangePasswordForm(forms.Form):
    password_current = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                       error_messages={'required': u'请输入原密码'})
    password_new = forms.CharField(min_length=6,
                                   widget=forms.PasswordInput(render_value=False),
                                   error_messages={'required': u'请输入新密码',
                                                   'min_length': u'新密码不应小于6位'})
    password_new_confirm = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                           error_messages={'required': u'请再次输入新密码'})

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_password_current(self):
        value = self.cleaned_data.get("password_current")
        if not self.user.check_password(value):
            raise forms.ValidationError(u"原密码错误")
        return value

    def clean_password_new_confirm(self):
        if not self.cleaned_data.get('password_new') ==\
                self.cleaned_data.get('password_new_confirm'):
            raise forms.ValidationError(u'两次输入的密码不匹配')
        return self.cleaned_data["password_new_confirm"]
