# -*-coding:utf-8 -*-
'''
Created on 2013-11-2

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

import os
import random

from django.conf import settings

from core.views import BaseView
from dshare.models import Photo, ShareCategory, Share
from django.templatetags.static import static
from core.http import JsonResponse
from common.paginator import Paginator


bg = static('site/v3/img/bgw.png')
image_boxes_1 = {
    'b1_1': {
        'html': ['<div class="photoBoxN fltlft">',
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="350" height="350">' % bg, '</div>'],
        'image_count': 1,
        'size': ['s350']
    },
    'b1_2': {
        'html': ['<div class="photoBoxN fltlft">',
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="175" height="175">' % bg,
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="175" height="175">' % bg,
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="175" height="175">' % bg,
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="175" height="175">' % bg, '</div>'],
        'image_count': 4,
        'size': ['s200c', 's200c', 's200c', 's200c']
    },
    'b1_3': {
        'html': ['<div class="photoBoxN fltlft">',
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="175" height="350">' % bg,
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="175" height="175">' % bg,
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="175" height="175">' % bg, '</div>'],
        'image_count': 3,
        'size': ['s175d', 's200c', 's200c']
    },
    'b1_4': {
        'html': ['<div class="photoBoxN fltlft">',
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="175" height="350">' % bg,
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="175" height="350">' % bg, '</div>'],
        'image_count': 2,
        'size': ['s175d', 's175d']
    }
}

image_boxes_2 = {
    'b2_1': {
        'html': ['<div class="photoBoxS fltlft">',
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="150" height="150">' % bg,
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="150" height="150">' % bg,
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="300" height="200">' % bg, '</div>'],
        'image_count': 3,
        'size': ['s200c', 's200c', 's300l'],
        'width': 300,
    },
    'b2_2': {
        'html': ['<div class="photoBoxS fltlft">',
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="300" height="200">' % bg,
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="300" height="150">' % bg, '</div>'],
        'image_count': 2,
        'size': ['s300l', 's300s'],
        'width': 300,
    },
    'b2_3': {
        'html': ['<div class="photoBoxS fltlft">',
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="300" height="150">' % bg,
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="300" height="200">' % bg, '</div>'],
        'image_count': 2,
        'size': ['s300s', 's300l'],
        'width': 300,
    },
    'b2_4': {
        'html': ['<div class="photoBoxB fltlft">',
                 '<img class="scrollLoading" data-url="{0}" src="%s" width="600" height="350">' % bg, '</div>'],
        'image_count': 1,
        'size': ['s600'],
        'width': 600,
    }
}


class GetPhotoHome(BaseView):
    template_name = 'dshare/photo.html'
    template_name_m = 'dshare/photo_m.html'
    rows_per_page = 10
    page_size = 24
    section_size = 240

    def get_session_key(self):
        return 'share:photo_list'

    def get_template_names(self):
        if self.request.session.get('VIEW_MODE') == 'mobile':
            return [self.template_name_m]
        return [self.template_name]

    def get_loader(self, photos):
        def loader(offset, num):
            return photos[offset:offset + num]
        return loader

    def generate_row(self):
        result = []

        box_name = random.choice(image_boxes_1.keys())
        result.append(image_boxes_1[box_name])

        total_width = 350
        while True:
            box_name = random.choice(image_boxes_2.keys())
            box = image_boxes_2[box_name]

            if total_width + box['width'] > 950:
                continue

            result.append(image_boxes_2[box_name])
            total_width += box['width']

            if total_width >= 950:
                break

        return random.sample(result, len(result))

    def generate_html(self, queryset):
        boxes = []
        for i in range(self.rows_per_page):
            boxes += self.generate_row()

        count = reduce(lambda x, y: x + y, [box['image_count'] for box in boxes])

        total, photos = queryset.count(), list(queryset[:count])
        result = []
        for box in boxes:
            html_list = box['html']
            result.append(html_list[0])
            for image_dom, size in zip(html_list[1: -1], box['size']):
                try:
                    photo = photos.pop()
                except IndexError:
                    break
                url = settings.MEDIA_URL + settings.PHOTO_ROOT +\
                      '/'.join([size, os.path.basename(photo.image.name)])
                result.append(image_dom.format(url))
            result.append(html_list[-1])
            if not photos:
                break

        return ''.join(result), count, total > count

    def get(self, request):
        photos = Photo.objects.all().order_by('created')

        if request.is_ajax() and request.session.get('VIEW_MODE') == 'mobile':
            paginator = Paginator(self.get_loader(photos), self.page_size,
                                  self.section_size, photos.count())
            page_instance = paginator.page(request, self.get_session_key())
            data = {
                'items': [os.path.basename(photo.image.name) for photo in page_instance.page_items],
                'has_next': page_instance.has_next()
            }
            return JsonResponse(status=1, data=data)

        on_tops = photos.filter(on_top=True)
        if on_tops.exists():
            top_photo = random.choice(on_tops)
            top_photo.image_url = settings.MEDIA_URL + settings.PHOTO_ROOT +\
                                  '/'.join(['s950', os.path.basename(top_photo.image.name)])
            photos = photos.exclude(id=top_photo.id)
        else:
            top_photo = None

        try:
            offset = int(request.GET.get('offset', 0))
        except:
            offset = 0

        html, used, has_next = self.generate_html(photos[offset:])
        context = {'top_photo': top_photo,
                   'html': html,
                   'has_next': has_next,
                   'offset': offset + used}

        if request.is_ajax():
            context.pop('top_photo')
            return JsonResponse(status=1, data=context)

        return self.render_to_response(context)


class GetShareHome(BaseView):
    template_name = 'dshare/interests.html'
    template_name_ajax = 'dshare/includes/inbox.html'
    template_name_m = 'dshare/interests_m.html'
    template_name_m_ajax = 'dshare/includes/inbox_m.html'
    page_size = 10
    section_size = 30

    def get_session_key(self):
        return 'share:list'

    def get_loader(self, shares):
        def loader(offset, num):
            return shares[offset:offset + num]
        return loader

    def get_template_names(self):
        if self.request.is_ajax():
            if self.request.session.get('VIEW_MODE') == 'mobile':
                return [self.template_name_m_ajax]
            return [self.template_name_m_ajax]
        print self.request.session.get('VIEW_MODE')
        if self.request.session.get('VIEW_MODE') == 'mobile':
            return [self.template_name_m]
        return [self.template_name]

    def get(self, request):
        shares = Share.objects.filter(is_published=True)
        paginator = Paginator(self.get_loader(shares), self.page_size,
                              self.section_size, shares.count())
        page_instance = paginator.page(request, self.get_session_key())

        context = {
            'page_instance': page_instance,
        }

        if request.is_ajax():
            html = self.render_to_response(context)
            html.render()
            data = {
                'html': html.content,
                'has_next': page_instance.has_next()
            }
            return JsonResponse(status=1, data=data)

        cates = ShareCategory.objects.all()
        context.update({
            'cates': cates,
            'cate_color_box_width': 79 * cates.count(),
        })
        return self.render_to_response(context)
