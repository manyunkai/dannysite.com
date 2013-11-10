#coding: utf-8

import json

from django.http.response import HttpResponse


class JsonResponse(HttpResponse):
    """
    The standard response for ueditor.
    """

    def __init__(self, state, data={}, *args, **kwargs):
        data['state'] = state

        super(JsonResponse, self).__init__(json.dumps(data),
                                           content_type='application/json',
                                           *args, **kwargs)


# 修正输入的文件路径,输入路径的标准格式：abc,不需要前后置的路径符号
def fix_file_path(path, instance=None):
    if callable(path):
        try:
            path = path(instance)
        except:
            path = ''

    if len(path) > 0:
        path = '%s/' % path.strip('/')

    return path


# 在上传的文件名后面追加一个日期时间 + 随机, 如abc.jpg --> abc_20120801202409.jpg
def GenerateRndFilename(filename):
    import datetime
    import random
    from os.path import splitext

    f_name, f_ext = splitext(filename)
    return "%s_%s%s%s" % (f_name, datetime.datetime.now().strftime("%Y%m%d_%H%M%S_"),
                          random.randrange(10,99), f_ext)


# 文件大小类
class FileSize():
    SIZE_UNIT={"Byte":1,"KB":1024,"MB":1048576,"GB":1073741824,"TB":1099511627776L}
    def __init__(self,size):
        self.size=long(FileSize.Format(size))

    @staticmethod
    def Format(size):
        import re
        if isinstance(size,int) or isinstance(size,long):
            return size
        else:
            if not isinstance(size,str):
                return 0
            else:
                oSize=size.lstrip().upper().replace(" ","")
                pattern=re.compile(r"(\d*\.?(?=\d)\d*)(byte|kb|mb|gb|tb)",re.I)
                match=pattern.match(oSize)
                if match:
                    m_size, m_unit=match.groups()
                    if m_size.find(".")==-1:
                        m_size=long(m_size)
                    else:
                        m_size=float(m_size)
                    if m_unit!="BYTE":
                        return m_size*FileSize.SIZE_UNIT[m_unit]
                    else:
                        return m_size
                else:
                    return 0

    #返回字节为单位的值
    @property
    def size(self):
        return self.size
    @size.setter
    def size(self,newsize):
        try:
            self.size=long(newsize)
        except:
            self.size=0

    #返回带单位的自动值
    @property
    def FriendValue(self):
        if self.size<FileSize.SIZE_UNIT["KB"]:
            unit="Byte"
        elif self.size<FileSize.SIZE_UNIT["MB"]:
            unit="KB"
        elif self.size<FileSize.SIZE_UNIT["GB"]:
            unit="MB"
        elif self.size<FileSize.SIZE_UNIT["TB"]:
            unit="GB"
        else:
            unit="TB"

        if (self.size % FileSize.SIZE_UNIT[unit])==0:
            return "%s%s" % ((self.size / FileSize.SIZE_UNIT[unit]),unit)
        else:
            return "%0.2f%s" % (round(float(self.size) /float(FileSize.SIZE_UNIT[unit]) ,2),unit)

    def __str__(self):
        return self.FriendValue

    #相加
    def __add__(self, other):
        if isinstance(other,FileSize):
            return FileSize(other.size+self.size)
        else:
            return FileSize(FileSize(other).size+self.size)
    def __sub__(self, other):
        if isinstance(other,FileSize):
            return FileSize(self.size-other.size)
        else:
            return FileSize(self.size-FileSize(other).size)
    def __gt__(self, other):
        if isinstance(other,FileSize):
            if self.size>other.size:
                return True
            else:
                return False
        else:
            if self.size>FileSize(other).size:
                return True
            else:
                return False
    def __lt__(self, other):
        if isinstance(other,FileSize):
            if other.size>self.size:
                return True
            else:
                return False
        else:
            if FileSize(other).size > self.size:
                return True
            else:
                return False
    def __ge__(self, other):
        if isinstance(other,FileSize):
            if self.size>=other.size:
                return True
            else:
                return False
        else:
            if self.size>=FileSize(other).size:
                return True
            else:
                return False
    def __le__(self, other):
        if isinstance(other,FileSize):
            if other.size>=self.size:
                return True
            else:
                return False
        else:
            if FileSize(other).size >= self.size:
                return True
            else:
                return False


def make_options(width=600, height=300, plugins=(), toolbars="normal",
                 file_path='', image_path='', scrawl_path='',
                 image_manager_path='', css='', options={}):
    import settings as u_settings

    image_path = image_path or u_settings.UEDITOR_SETTINGS['images_upload'].get('path', '')
    file_path = file_path or u_settings.UEDITOR_SETTINGS['files_upload'].get('path', '')

    o_image_manager_path = image_manager_path or u_settings.UEDITOR_SETTINGS['image_manager'].get('path', '')
    if o_image_manager_path:
        image_manager_path = fix_file_path(o_image_manager_path)
    else:
        image_manager_path = image_path

    o_scrawl_path = scrawl_path or u_settings.UEDITOR_SETTINGS['scrawl_upload'].get('path', '')
    if o_scrawl_path:
        scrawl_path = fix_file_path(o_scrawl_path)
    else:
        scrawl_path = image_path

    return {'css': css, 'plugins': plugins, 'toolbars': toolbars,
            'options': options, 'width': width, 'height': height,
            'image_path': fix_file_path(image_path),
            'file_path': fix_file_path(file_path),
            'image_manager_path': image_manager_path,
            'scrawl_path': scrawl_path,
            'o_image_path': image_path,
            'o_file_path': file_path,
            'o_image_manager_path': o_image_manager_path,
            'o_scrawl_path': o_scrawl_path}
