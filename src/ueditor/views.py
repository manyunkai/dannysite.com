#coding:utf-8

import os
import json
import uuid
import settings as u_settings

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.views.generic.base import View
from django.conf import settings
from django.utils.decorators import method_decorator

from core.views import ImageAutoHandleMixin, str_crc32
from ueditor.utils import JsonResponse
from common.log_utils import set_log
from common.htmlparser import ImageParser
from common.image_utils import BaseImageParser


class UploadImage(View, ImageAutoHandleMixin):
    image_conf = u_settings.IMAGES_CONF
    save_origin = True
    save_dims = False

    files_rev_key = 'upfile'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UploadImage, self).dispatch(*args, **kwargs)

    def post(self, request, action, uploadpath):
        # TODO ... 加入对传入的 uploadpath 的支持
        if not request.user.is_authenticated():
            return JsonResponse(state='Permission denied.')

        response = super(UploadImage, self).post(request)
        response = json.loads(response.content)
        if response.get('status'):
            data = {
                'url': response.get('images')[0],    # 保存后的文件名称
                'title': response.get('images')[0],  # 文件描述，对图片来说在前端会添加到title属性上
            }
            if action == 'scrawlbg':
                # 上传涂鸦背景
                text = u'<script>parent.ue_callback(\'{0}\',\'{1}\');</script>'
                return HttpResponse(text.format(data['url'], 'SUCCESS'))
            # 一般图片上传返回
            return JsonResponse(state='SUCCESS', data=data)
        return JsonResponse(state=response.get('message'))


class UploadScrawl(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UploadScrawl, self).dispatch(*args, **kwargs)

    def save(self, content, uploadpath):
        # TODO ... 加入对传入的 uploadpath 的支持
        import base64

        filename = str(uuid.uuid1()) + '.png'
        path = os.path.join(os.path.join(settings.MEDIA_ROOT, os.path.dirname(uploadpath)))

        try:
            if not os.path.exists(path):
                os.makedirs(path)

            f = open(os.path.join(path, filename), 'wb')
            f.write(base64.decodestring(content))
            f.close()
        except Exception, e:
            set_log('error', str(e))
            return JsonResponse(state='ERROR')
        return JsonResponse(state='SUCCESS', data={'url': filename})

    def post(self, request, uploadpath):
        if request.GET.get('action') == 'tmpImg':
            # 背景上传
            return UploadImage.as_view()(request, 'scrawlbg', uploadpath)
        else:
            # 处理涂鸦合成相片上传
            return self.save(request.POST.get('content'), uploadpath)


class ImageManager(View):
    """
    View for Image Manager.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ImageManager, self).dispatch(*args, **kwargs)

    def list_dir(self, path):
        file_names = []
        for f in os.listdir(path):
            ext = os.path.splitext(f)[1][1:]
            if ext in u_settings.UEDITOR_SETTINGS['images_upload']['allow_type']:
                file_names.append(f)
        return 'ue_separate_ue'.join(file_names)

    def post(self, request, imagepath):
        if not request.user.is_authenticated():
            return JsonResponse(state='ERROR')

        # 取得动作
        if request.GET.get('action', 'get') == 'get':
            target_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT,
                                           os.path.dirname(imagepath)))

            if not os.path.exists(target_path):
                os.makedirs(target_path)

            files = self.list_dir(target_path)

            return HttpResponse(files, mimetype='application/json')


class UploadFile(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UploadFile, self).dispatch(*args, **kwargs)

    def save(self, upfile, path):
        try:
            f = open(path, 'wb')
            for chunk in upfile.chunks():
                f.write(chunk)
        except Exception, e:
            set_log('error', u'Error in saving uploading file:' + e.message)
            return False
        else:
            return True
        finally:
            f.close()

    def post(self, request, uploadpath):
        if not request.user.is_authenticated():
            return JsonResponse(state='Permission denied.')

        upfile = request.FILES.get('upfile', None)
        if not upfile:
            return JsonResponse(state='No file found.')

        ext = os.path.splitext(upfile.name)[1]

        f_settings = u_settings.UEDITOR_SETTINGS['files_upload']
        if not ext.lstrip('.') in f_settings['allow_type']:
            return JsonResponse(state='This type of file is not allowed.')
        if f_settings['max_size'] and upfile.size > f_settings['max_size']:
            return JsonResponse(state='This type of file is not allowed.')

        path = os.path.normpath(os.path.join(u_settings.UPLOAD_FILES_ROOT,
                                             os.path.dirname(uploadpath)))
        if not os.path.exists(path):
            os.mkdir(path)

        if self.save(upfile, os.path.join(path, upfile.name)):
            data = {
                'url': upfile.name,         # 保存后的文件名称
                'original': upfile.name,    # 原始文件名
                'filetype': ext,
            }
            # 上传状态，成功时返回state为SUCCESS，其他任何值将原样返回至图片上传框中
            return JsonResponse(state='SUCCESS', data=data)
        return JsonResponse(state='An Error Occurred, please try again later.')


class CatchRemoteImage(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CatchRemoteImage, self).dispatch(*args, **kwargs)

    def get_image(self, url):
        print url
        status, data = ImageParser(url).load()
        print status, data
        if not status:
            set_log('error', data)
            return None
        return data

    def save(self, image, basename):
        new = BaseImageParser([image], u_settings.IMAGES_CONF)
        if new.is_valid() and new.parse():
            images = new.save([basename])
            if images:
                return images[0]
        set_log('error', ' '.join([new.error, new.sys_error]))
        return None

    def post(self, request, imagepath):
        url = request.POST.get('upfile', None)
        if not url:
            return JsonResponse(state='No url supplied.')

        fetched = []
        for one in url.split('ue_separate_ue'):
            filename = os.path.basename(one)
            if not os.path.splitext(filename)[1] in u_settings.IMAGES_CONF['limits']['formats']:
                return JsonResponse(state='This type of image is not allowed.')

            image = self.get_image(one)
            if not image:
                return JsonResponse(state='Fetch error.')

            new_name = str_crc32(filename) + '.jpg'
            if self.save(image, new_name):
                fetched.append(new_name)

        if fetched:
            data = {
                'url': 'ue_separate_ue'.join(fetched),           # 新地址一ue_separate_ue新地址二
                'srcUrl': url,                                   # 原始地址一ue_separate_ue原始地址二
                'tip': 'Fetch succeed.'                          # 状态提示
            }
            return JsonResponse(state='SUCCESS', data=data)
        return JsonResponse(state='Fetch error.')
