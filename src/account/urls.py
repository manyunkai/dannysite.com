#coding=utf8

from django.conf.urls import patterns, url
from account.views import Login, Signup, Logout, ConfirmEmail, ResetPassword,\
    ResetPasswordToken, ChangePassword


urlpatterns = patterns("",
    url(r"^login/$", Login.as_view(), name="acct_login"),
    #url(r"^signup/$", Signup.as_view(), name="acct_signup"),
    url(r"^logout/$", Logout.as_view(), name="acct_logout"),
    #url(r"^confirm_email/(?P<key>\w+)/$", ConfirmEmail.as_view(), name="acct_confirm_email"),
    #url(r"^password/change/$", ChangePassword.as_view(), name="acct_password"),
    #url(r"^password/reset/$", ResetPassword.as_view(), name="acct_password_reset"),
    #url(r"^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$", ResetPasswordToken.as_view(), name="acct_password_reset_token"),
)
