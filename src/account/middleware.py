import re

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import urlquote

from django.contrib.auth import REDIRECT_FIELD_NAME


class AuthenticatedMiddleware(object):
    def __init__(self, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
        if login_url is None:
            login_url = settings.LOGIN_URL
        self.redirect_field_name = redirect_field_name
        self.login_url = login_url
        self.exemptions = [
            r"^%s" % settings.MEDIA_URL,
            r"^%s" % settings.STATIC_URL,
            r"^%s$" % login_url,
        ] + getattr(settings, "AUTHENTICATED_EXEMPT_URLS", [])

    def process_request(self, request):
        for exemption in self.exemptions:
            if re.match(exemption, request.path):
                return None
        if not request.user.is_authenticated():
            path = urlquote(request.get_full_path())
            tup = (self.login_url, self.redirect_field_name, path)
            return HttpResponseRedirect("%s?%s=%s" % tup)
