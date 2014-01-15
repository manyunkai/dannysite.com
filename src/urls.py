from functools import partial

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from core.url_wrapper import required
from dsite.view import About, Index, Feedback
from dblog.sitemap import BlogSitemap
admin.autodiscover()

sitemaps = {
    'blog': BlogSitemap
}

urlpatterns = patterns('',
    # Examples:
    url(r'^$', Index.as_view(), name='home'),
    url(r'^about/$', About.as_view(), name='about'),
    url(r'^about/feedback/$', Feedback.as_view(), name='feedback'),
    url(r'^ueditor/', include('ueditor.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^blog/', include('dblog.urls')),
    url(r'^photo/', include('dshare.urls.photo')),
    url(r'^interest/', include('dshare.urls.share')),
    url(r'^cloud/', include('dstore.urls')),

    url(r'^account/', include('account.urls')),
    url(r'^mail/', include('mail.urls')),
    url(r'^grappelli/', include('grappelli.urls')),

    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps})
)

urlpatterns += required(
    partial(login_required),
    patterns('',
        url(r"^admin/", include(admin.site.urls)),
        #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    )
)

if settings.DEBUG:
    urlpatterns += patterns("",
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}
        ),
    )
