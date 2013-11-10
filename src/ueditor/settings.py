#coding:utf-8

# 全局设置

from django.conf import settings as g_settings
import os

# 工具栏样式，可以添加任意多的模式
TOOLBARS_SETTINGS = {
    'mini': [['source', '|', 'undo', 'redo', '|', 'bold',
              'italic', 'underline', 'formatmatch',
              'autotypeset', '|', 'forecolor', 'backcolor',
              '|', 'link', 'unlink', '|', 'insertimage', 'attachment']],
    'normal': [['source', '|', 'undo', 'redo', '|', 'bold', 'italic',
                'underline', 'removeformat', 'formatmatch', 'autotypeset',
                '|', 'forecolor', 'backcolor', '|', 'link', 'unlink',
                '|', 'insertimage', 'emotion', 'attachment', '|',
                'inserttable', 'deletetable', 'insertparagraphbeforetable',
                'insertrow', 'deleterow', 'insertcol', 'deletecol',
                'mergecells', 'mergeright', 'mergedown', 'splittocells',
                'splittorows', 'splittocols']],
}

DEFAULT_TOOLBARS = 'full'

# 引入的第三方插件
THIRD_PARTY_PLUGINS = ()

# 允许上传的图片类型
UPLOAD_IMAGES_SETTINGS = {
    'allow_type': 'jpg, bmp, png, gif, jpeg',   # 文件允许格式
    'path': 'images/uploads/',
    'max_size': 0                               # 文件大小限制，单位KB, 0为不限
}

# 图片设置
IMAGES_CONF = {
    'limits': {
        'formats': ('.jpg', '.gif', '.jpeg', '.bmp', '.png'),  # 允许上传的文件类型
        'max_file_size': 5 * 1024 * 1024,                      # 上传的文件大小限制
    },
    'origin': {
        'dir': os.path.join(g_settings.MEDIA_ROOT, 'images/uploads/')
    },
    'dims': {
#         'normal': {
#             'action': 'scale',
#             'size': (100, 100),                       # 定义普通缩放的图片大小
#             'dir': os.path.join(PROFILE_ROOT, 'normal'),
#             'quality': 100,
#         },
    },
}

# 允许上传的附件类型
UPLOAD_FILES_ROOT = 'E:\\MyWork\\Designations\\repo\\dannysite\\files'
UPLOAD_FILES_SETTINGS = {
    'allow_type': 'zip, rar, doc, docx, xls, xlsx, ppt, pptx, swf, dat, avi, rmvb, txt, pdf',         #文件允许格式
    'path': '/downloads/',
    'max_size': 0                               # 文件大小限制, 0为不限
}

# 涂鸦上传
SCRAWL_FILES_SETTINGS = {
    'path': 'images/uploads/'
}

# 图片管理器地址
IMAGE_MANGER_SETTINGS = {
    'path': ''             # 图片管理器的位置,如果没有指定，默认跟图片路径上传一样
}

UEDITOR_SETTINGS = {
    'toolbars': TOOLBARS_SETTINGS,
    'images_upload': UPLOAD_IMAGES_SETTINGS,
    'files_upload': UPLOAD_FILES_SETTINGS,
    'image_manager': IMAGE_MANGER_SETTINGS,
    'scrawl_upload': SCRAWL_FILES_SETTINGS
}


# 更新配置：从用户配置文件settings.py重新读入配置UEDITOR_SETTINGS,
def update_user_settings():
    UEDITOR_SETTINGS.update(getattr(g_settings, 'UEDITOR_SETTINGS', {}))


# 取得配置项参数
def get_setting(key, default=None):
    return UEDITOR_SETTINGS.get(key, default)

# 读取用户Settings文件覆盖默认配置
update_user_settings()
