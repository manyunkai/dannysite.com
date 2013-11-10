# -*-coding:utf-8 -*-
'''
Created on 2013-11-8

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from dblog.models import Blog


class BlogSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.8

    def items(self):
        return Blog.objects.filter(is_draft=False, is_published=True)

    def lastmod(self, obj):
        return obj.created

    def location(self, obj):
        return reverse('blog_detail', args=[obj.id])
