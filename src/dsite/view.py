# -*-coding:utf-8 -*-
'''
Created on 2013-10-30

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

import os
import random

from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from core.views import AccessAuthMixin
from dsite.forms import FeedbackForm
from dsite.models import Focus
from dshare.models import Photo
from core.http import JsonResponse
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from dblog.models import Blog, Category


class Index(TemplateView):
    template_name = 'index.html'
    template_name_mobile = 'index_m.html'

    def get_template_names(self):
        if self.request.session.get('VIEW_MODE') == 'mobile':
            return [self.template_name_mobile]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)

        focuses = Focus.objects.filter(is_shown=True).order_by('?')
        context['focus'] = focuses[0] if focuses.exists() else None

        blogs = Blog.objects.all()
        context['latest_blogs'] = blogs[:5]
        context['hottest_blogs'] = random.sample(Blog.objects.all().order_by('-click_count', '-created')[:15], blogs.count() if blogs.count() < 5 else 5)
        context['hottest_cates'] = Category.objects.all().order_by('-count')[:5]

        photos = Photo.objects.all()[:4]
        if photos.count() == 4:
            context['latest_photo'] = photos[0]
            context['photos'] = [os.path.basename(photo.image.name) for photo in photos]
        return context


class About(TemplateView):
    template_name = 'about.html'
    template_name_mobile = 'about_m.html'

    def get_template_names(self):
        if self.request.session.get('VIEW_MODE') == 'mobile':
            return [self.template_name_mobile]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super(About, self).get_context_data(**kwargs)
        context['form'] = FeedbackForm()
        return context


class Feedback(FormView, AccessAuthMixin):
    form_class = FeedbackForm
    http_method_names = ['post']

    def form_valid(self, form):
        fb = form.save()
        fb.ip = self.get_client_ip(self.request)
        fb.save()

        return JsonResponse(status=1)

    def form_invalid(self, form):
        # Refresh captcha
        key = CaptchaStore.generate_key()
        url = captcha_image_url(key)
        return JsonResponse(status=0, msg=form.errors.popitem()[1],
                            data={'captcha': [key, url]})
