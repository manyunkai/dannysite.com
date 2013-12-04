# -*-coding:utf-8 -*-
'''
Created on 2013-10-24

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

import urlparse

from django.views.generic.edit import FormView
from django.http.response import Http404, HttpResponseRedirect
from django.db.models.expressions import F
from django.contrib.sites.models import get_current_site
from django.views.generic.base import View
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q

from core.views import BaseView, AccessAuthMixin
from common.paginator import Paginator
from dblog.forms import CommentForm
from dblog.models import Category, Tag, Blog
from core.http import JsonResponse
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from core.models import DComment
from dsite.models import Link


class BlogBase(BaseView):
    tags_shown_count = 50

    def get_context_data(self, extra_context):
        context = {
            'categories': Category.objects.exclude(count=0),
            'tags': Tag.objects.exclude(count=0).order_by('?')[:self.tags_shown_count],
            'pblogs': Blog.objects.all().order_by('-click_count', '-created')[:8],
            'links': Link.objects.all()
        }
        context.update(extra_context)
        return context


class GetHome(BlogBase):
    template_name = 'dblog/index.html'
    template_name_m = 'dblog/index_m.html'
    page_size = 5
    section_size = 10

    def get_session_key(self):
        return 'blog:list'

    def get_loader(self, blogs):
        def loader(offset, num):
            return blogs[offset:offset + num]
        return loader

    def get_template_names(self):
        if self.request.session.get('VIEW_MODE') == 'mobile':
            return [self.template_name_m]
        return [self.template_name]

    def get_queryset(self, cate_id, tag_id, q):
        if cate_id:
            if not cate_id.isdigit():
                raise Http404

            try:
                cate = Category.objects.get(id=cate_id)
            except Category.DoesNotExist:
                raise Http404

            blogs = Blog.objects.filter(cate=cate)
            filter = cate.name
        elif tag_id:
            if not tag_id.isdigit():
                raise Http404

            try:
                tag = Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                raise Http404

            blogs = tag.blog_set.all()
            filter = tag.name
        elif q:
            blogs = Blog.objects.filter(Q(title__icontains=q) |
                                        Q(tags__name__icontains=q) |
                                        Q(content__icontains=q) |
                                        Q(cate__name__icontains=q)).distinct()
            filter = q
        else:
            blogs = Blog.objects.all()
            filter = None
        return blogs.filter(is_published=True, is_draft=False), filter

    def get_url_prefix(self, full_path, cate_id, tag_id, q):
        query = []
        if cate_id:
            query.append('cat={0}'.format(cate_id))
        elif tag_id:
            query.append('tag={0}'.format(tag_id))
        elif q:
            query.append(u'search={0}'.format(q))
        query.append('page=')

        parsed_url = urlparse.urlparse(full_path)

        return urlparse.urlunparse((parsed_url.scheme,
                                    parsed_url.netloc,
                                    parsed_url.path,
                                    parsed_url.params,
                                    '&'.join(query), ''))

    def get(self, request):
        cate_id = request.GET.get('cat', '')
        tag_id = request.GET.get('tag', '')
        q = request.GET.get('search', '')

        blogs, filter = self.get_queryset(cate_id, tag_id, q)
        paginator = Paginator(self.get_loader(blogs), self.page_size,
                              self.section_size, blogs.count())
        page_instance = paginator.page(request, self.get_session_key())

        url_prefix = self.get_url_prefix(request.get_full_path(),
                                         cate_id, tag_id, q)

        extra_context = {'blogs': page_instance.page_items,
                         'filter': filter,
                         'page_instance': page_instance,
                         'page_range': page_instance.get_page_range(2, 4),
                         'url_prefix': url_prefix}

        return self.render_to_response(self.get_context_data(extra_context))


class GetDetail(BlogBase, AccessAuthMixin):
    template_name = 'dblog/detail.html'
    template_name_m = 'dblog/detail_m.html'
    max_recommended_count = 8

    def get_context_data(self, extra_context):
        context = super(GetDetail, self).get_context_data(extra_context)
        context['form'] = CommentForm()
        return context

    def get_template_names(self):
        if self.request.session.get('VIEW_MODE') == 'mobile':
            return [self.template_name_m]
        return [self.template_name]

    def get_recommends(self, curr):
        return Blog.objects.filter(Q(tags__in=curr.tags.all()) |
                                   Q(cate=curr.cate),
                                   is_draft=False,
                                   is_published=True).exclude(id=curr.id).distinct()[:self.max_recommended_count]

    def get(self, request, bid):
        try:
            blog = Blog.objects.get(id=bid, is_published=True, is_draft=False)
        except Blog.DoesNotExist:
            raise Http404

        blog.click(self.get_client_ip(request))
        blog.tag_list = [tag.name for tag in blog.tags.all()]

        relates = blog.topic.blog_set.filter(is_draft=False, is_published=True).exclude(id=blog.id) if blog.topic else []

        extra_context = {
            'blog': blog,
            'relates': relates,
            'recommends': self.get_recommends(blog),
            'comments': DComment.objects.get_comments(blog)
        }
        return self.render_to_response(self.get_context_data(extra_context))


class Comment(FormView, AccessAuthMixin):
    form_class = CommentForm
    http_method_names = ['post']
    template_name_comment = 'dblog/includes/cmtdisplaybox.html'
    template_name_reply = 'dblog/includes/replydisplaybox.html'
    template_name_comment_m = 'dblog/includes/cmtdisplaybox_m.html'
    template_name_reply_m = 'dblog/includes/replydisplaybox_m.html'

    def post(self, request, bid, *args, **kwargs):
        try:
            self.blog = Blog.objects.get(id=bid, is_published=True, is_draft=False)
        except Blog.DoesNotExist:
            raise Http404

        return super(Comment, self).post(request, *args, **kwargs)

    def get_template_name(self, is_related):
        if is_related:
            if self.request.session.get('VIEW_MODE') == 'mobile':
                return self.template_name_reply_m
            return self.template_name_reply
        else:
            if self.request.session.get('VIEW_MODE') == 'mobile':
                return self.template_name_comment_m
            return self.template_name_comment

    def form_valid(self, form):
        comment = form.save(self.blog, self.get_client_ip(self.request),
                            get_current_site(self.request))

        self.blog.comment_count = F('comment_count') + 1
        self.blog.save()

        self.template_name = self.get_template_name(comment.related)
        if comment.related:
            context = {'reply': comment}
        else:
            context = {'comment': comment}

        html = self.render_to_response(context)
        html.render()
        data = {
            'html': html.content
        }

        return JsonResponse(status=1, data=data)

    def form_invalid(self, form):
        # Refresh captcha
        key = CaptchaStore.generate_key()
        url = captcha_image_url(key)
        return JsonResponse(status=0, msg=form.errors.popitem()[1],
                            data={'captcha': [key, url]})


class OldDetail(View):
    """
    Compatible with the old version.
    """

    def get(self, request):
        bid = request.GET.get('id')
        if bid:
            return HttpResponseRedirect(reverse('blog_detail', args=[bid]))
        raise Http404
