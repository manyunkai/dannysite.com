# -*-coding:utf-8 -*-
'''
Created on 2013-7-29
@author: Danny<manyunkai@hotmail.com>

Copyright (C) 2012-2014 DannyWork Project
'''

import urllib2
import ImageFile
import chardet
from bs4 import BeautifulSoup
import platform
py_ver = int(''.join(platform.python_version().split('.')))
if py_ver < 273:
    try:
        import html5lib
    except ImportError:
        raise ImportError('Crawler needs "html5lib" for parsing HTML or update your python to 2.7.3 or newer.')


class BaseParser(object):
    NET_ERROR = -1
    NOT_FOUND = 0
    SUCCESS = 1
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36'}

    def __init__(self, url):
        self.url = url

    def handle(self):
        req = urllib2.Request(self.url, headers=self.headers)
        try:
            handle = urllib2.urlopen(req)
            if not handle.getcode() == 200:
                return self.NOT_FOUND
            self.object = handle
            return self.SUCCESS
        except Exception, e:
            return 'Error: Open Url failed: {0}'.format(e)

    def fetch(self):
        if hasattr(self, 'object'):
            return self.object.read()
        return None


class ImageParser(BaseParser):
    def __init__(self, url):
        self.url = url
        super(ImageParser, self).__init__(url=url)

    def load(self):
        if not self.handle() == self.SUCCESS:
            return False, 'Loading failed from url in ImageParser.'
        try:
            parser = ImageFile.Parser()
            for fragment in self.object:
                parser.feed(fragment)
            img = parser.close()
        except IOError, e:
            return False, "Error in Paring Image: {0}".format(e)

        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        return True, img


class HTMLParser(BaseParser):
    def __init__(self, url, encoding='gbk'):
        super(HTMLParser, self).__init__(url=url)
        self.data = None
        self.error = None
        self.encoding = encoding

    def load(self):
        code = self.handle()
        if code == self.SUCCESS:
            data = self.fetch()
            encoding = chardet.detect(data).get('encoding') or self.object.info().getparam('charset')
            encoding = 'gbk' if not encoding or encoding.lower() == 'gb2312' else encoding
            if py_ver < 273:
                self._data = BeautifulSoup(data, 'html5lib',
                                           from_encoding=encoding)
            else:
                self._data = BeautifulSoup(data, from_encoding=encoding)
            return True
        self.error = 'URL parsed Error.'
        return False
