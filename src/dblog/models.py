# -*-coding:utf-8 -*-
'''
Created on 2013-10-24

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

from django.db import models

from user.models import User
from django.db.models.expressions import F
from django.db.models.signals import m2m_changed, pre_save, pre_delete
from django.conf import settings


COUNTER_CACHE_TIMEOUT = 24 * 60 * 60


class NoCacheKeySupplied(BaseException):
    pass


class BaseModel(models.Model):
    name = models.CharField(u'名称', max_length=30)
    count = models.IntegerField(u'引用', default=0)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    def __unicode__(self):
        return self.name

    def incr(self, num=1):
        self.count = F('count') + num
        self.save()

    def decr(self, num=1):
        self.count = F('count') - num
        self.save()

    class Meta:
        abstract = True
        ordering = ['-created']


class Tag(BaseModel):

    class Meta:
        db_table = 'dblog_tag'
        verbose_name = u'标签'
        verbose_name_plural = u'标签'


class Category(BaseModel):

    class Meta:
        db_table = 'dblog_category'
        verbose_name = u'分类'
        verbose_name_plural = u'分类'


class Theme(BaseModel):

    class Meta:
        db_table = 'dblog_theme'
        verbose_name = u'主题'
        verbose_name_plural = u'主题'


class Blog(models.Model):
    title = models.CharField(u'标题', max_length=100)
    theme = models.ForeignKey(Theme, verbose_name=u'主题')
    cate = models.ForeignKey(Category, verbose_name=u'分类')
    author = models.ForeignKey(User, verbose_name=u'作者')
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=u'标签')
    content = models.TextField(u'正文')

    is_draft = models.BooleanField(u'草稿状态', default=False)
    is_published = models.BooleanField(u'公开状态', default=True)

    click_count = models.IntegerField(u'点击量', default=0, editable=False)
    comment_count = models.IntegerField(u'评论数', default=0, editable=False)

    def __unicode__(self):
        return unicode(self.title)

    def chg_pub_status(self):
        self.is_published = self.is_published == False
        self.save()

    def chg_draft_status(self):
        self.is_draft = self.is_draft == False
        self.save()

    def click(self, ip_addr):
        from core.utils import get_redis

        cache_key = settings.BLOG_VISITORS_CACHE_KEY.format(self.id)
        conn = get_redis()
        if int(conn.zincrby(cache_key, ip_addr)) == 1:
            self.click_count = F('click_count') + 1
            self.save()

        if conn.zcard(cache_key) == 1:
            conn.expire(cache_key, settings.BLOG_VISITORS_CACHE_TIMEOUT)

    class Meta:
        ordering = ['-created']
        db_table = 'dblog_blog'
        verbose_name = u'博客'
        verbose_name_plural = u'博客'


def handle_in_batches(instances, method):
    for instance in instances:
        getattr(instance, method)()


def tags_changed(sender, **kwargs):
    if kwargs.get('action') == 'pre_clear':
        handle_in_batches(kwargs.get('instance').tags.all(), 'decr')
    elif kwargs.get('action') == 'post_remove':
        handle_in_batches(Tag.objects.filter(id__in=kwargs.get('pk_set')), 'decr')
    elif kwargs.get('action') == 'post_add':
        handle_in_batches(Tag.objects.filter(id__in=kwargs.get('pk_set')), 'incr')


def blog_pre_save(sender, **kwargs):
    curr = kwargs.get('instance')
    try:
        prev = Blog.objects.get(id=curr.id)
    except Blog.DoesNotExist:
        if not curr.is_draft or curr.is_published:
            curr.theme.incr()
            curr.cate.incr()
    else:
        for item in ['theme', 'cate']:
            prev_ps = prev.is_published and not prev.is_draft
            curr_ps = curr.is_published and not curr.is_draft

            prev_obj, curr_obj = getattr(prev, item), getattr(curr, item)

            if prev_ps and not curr_ps or prev_ps and not prev_obj == curr_obj:
                prev_obj.decr()

            if curr_ps:
                curr_obj.incr()


def blog_pre_delete(sender, **kwargs):
    instance = kwargs.get('instance')
    for item in ['theme', 'cate']:
        getattr(instance, item).decr()
    handle_in_batches(instance.tags.all(), 'decr')

m2m_changed.connect(tags_changed, sender=Blog.tags.through)
pre_save.connect(blog_pre_save, sender=Blog)
pre_delete.connect(blog_pre_delete, sender=Blog)
