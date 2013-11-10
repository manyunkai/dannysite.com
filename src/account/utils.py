# -*-coding:utf-8 -*-

import functools
import hashlib
import random
from urlparse import urlunparse, urlparse

from django.conf import settings
from django.contrib.auth import login
from django.core.exceptions import SuspiciousOperation
from django.core import urlresolvers
from django.http.response import HttpResponseRedirect
from django.http.request import QueryDict

from account.signals import user_logged_in, password_changed


def default_redirect(request, fallback_url, **kwargs):
    redirect_field_name = kwargs.get("redirect_field_name", "next")
    next_url = request.REQUEST.get(redirect_field_name)
    if not next_url:
        # try the session if available
        if hasattr(request, "session"):
            session_key_value = kwargs.get("session_key_value", "redirect_to")
            if session_key_value in request.session:
                next_url = request.session[session_key_value]
                del request.session[session_key_value]
    is_safe = functools.partial(
        ensure_safe_url,
        allowed_protocols=kwargs.get("allowed_protocols"),
        allowed_host=request.get_host()
    )

    if next_url and is_safe(next_url):
        return next_url
    else:
        # assert the fallback URL is safe to return to caller. if it is
        # determined unsafe then raise an exception as the fallback value comes
        # from the a source the developer choose.
        is_safe(fallback_url, raise_on_fail=True)
        return fallback_url


def user_display(user):
    func = getattr(settings, "ACCOUNT_USER_DISPLAY", lambda user: user.username)
    return func(user)


def ensure_safe_url(url, allowed_protocols=None, allowed_host=None, raise_on_fail=False):
    if allowed_protocols is None:
        allowed_protocols = ["http", "https"]
    parsed = urlparse(url)
    # perform security checks to ensure no malicious intent
    # (i.e., an XSS attack with a data URL)
    safe = True
    if parsed.scheme and parsed.scheme not in allowed_protocols:
        if raise_on_fail:
            raise SuspiciousOperation("Unsafe redirect to URL with protocol '{0}'".format(parsed.scheme))
        safe = False
    if allowed_host and parsed.netloc and parsed.netloc != allowed_host:
        if raise_on_fail:
            raise SuspiciousOperation("Unsafe redirect to URL not matching host '{0}'".format(allowed_host))
        safe = False
    return safe


def random_token(extra=None, hash_func=hashlib.sha256):
    if extra is None:
        extra = []
    bits = extra + [str(random.SystemRandom().getrandbits(512))]
    return hash_func("".join(bits).encode("utf-8")).hexdigest()


def has_openid(request):
    """
    Given a HttpRequest determine whether the OpenID on it is associated thus
    allowing caller to know whether OpenID is good to depend on.
    """
    from django_openid.models import UserOpenidAssociation
    for association in UserOpenidAssociation.objects.filter(user=request.user):
        if association.openid == unicode(request.openid):
            return True
    return False


def handle_redirect_to_login(request, **kwargs):
    login_url = kwargs.get("login_url")
    redirect_field_name = kwargs.get("redirect_field_name")
    next_url = kwargs.get("next_url")
    if login_url is None:
        login_url = settings.ACCOUNT_LOGIN_URL
    if next_url is None:
        next_url = request.get_full_path()
    try:
        login_url = urlresolvers.reverse(login_url)
    except urlresolvers.NoReverseMatch:
        if callable(login_url):
            raise
        if "/" not in login_url and "." not in login_url:
            raise
    url_bits = list(urlparse(login_url))
    if redirect_field_name:
        querystring = QueryDict(url_bits[4], mutable=True)
        querystring[redirect_field_name] = next_url
        url_bits[4] = querystring.urlencode(safe="/")
    return HttpResponseRedirect(urlunparse(url_bits))


def perform_login(request, user):
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    login(request, user)


def change_password(user, new_pass):
    user.set_password(new_pass)
    user.save()
    password_changed.send(sender=user.__class__, user=user)


