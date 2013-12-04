# -*-coding:utf-8 -*-
'''
Created on 2013-10-24

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

import math


class PagingError(BaseException):
    pass


class PageInstance(object):
    def __init__(self, page_items, page_range, current_page):
        self.page_items = page_items
        self.page_range = page_range
        self.current_page = current_page

        self.first_page = page_range[0]
        self.last_page = page_range[-1]

    def get_page_range(self, left, right):
        index = self.page_range.index(self.current_page)
        left_index = index - left - 1
        if left_index < 0:
            left_index = 0
        right_index = index + right
        return self.page_range[left_index:right_index]

    def has_previous(self):
        return True if self.page_range.index(self.current_page) else False

    def has_next(self):
        return True if not self.page_range[-1] == self.current_page else False

    def next(self):
        return self.current_page + 1

    def prev(self):
        return self.current_page - 1

    def has_other_pages(self):
        return len(self.page_range) > 1

    def __unicode__(self):
        string = 'PageInstance:\n  page_items: {0}\n  page_range: {1}\n  current_page: {2}'
        return string.format(self.page_items,
                             self.page_range,
                             self.current_page)


class Paginator(object):
    def __init__(self, loader, page_size, section_size, total):
        self.loader = loader

        if section_size % page_size:
            raise PagingError('The section_size must be divisible by page_size.')

        self.page_size = page_size
        self.section_size = section_size
        self.section_page_num = section_size / page_size

        self.total = total

        max_page = int(math.ceil(float(total) / page_size)) - 1
        self.max_page = 0 if max_page < 0 else max_page

    def get_page(self, request):
        try:
            return int(request.GET.get('page', 1))
        except:
            return 1

    def page(self, request, session_key, page=None):
        session_dict = request.session.get(session_key, {})
        prev_count = session_dict.get('count')
        if not page:
            page = self.get_page(request)

        if not prev_count or page == 1:
            prev_count = session_dict['count'] = self.total

        offset = self.total - prev_count
        offset = 0 if offset < 0 else offset

        page -= 1
        if page < 0:
            page = 0
        elif page > self.max_page:
            page = self.max_page
        original = page + 1

        section = page / self.section_page_num
        section = 0 if section < 0 else section
        page = page - self.section_page_num * section

        paging = {} if section == 0 and page == 0 else session_dict.get('paging', {})

        if not paging or not paging.get(section):
            offset = offset + self.section_size * section
            paging[section] = self.loader(offset, self.section_size)
            session_dict['paging'] = paging

        request.session[session_key] = session_dict

        #print 'Session_dict:', session_dict
        #print 'Session_size - pagenum:', self.section_size, self.section_page_num

        return PageInstance(paging[section][self.page_size * page:self.page_size * (page + 1)],
                            range(1, self.max_page + 2), original)
