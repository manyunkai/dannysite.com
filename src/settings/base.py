# -*-coding:utf-8 -*-
# Django settings for dannysite project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',     # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dannysite',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                           # Set to empty string for default.
    }
}

AUTH_USER_MODEL = 'user.User'
AUTHENTICATION_BACKENDS = ('user.backends.AuthenticationBackend',)

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'
TIME_FORMAT = 'H:i:s'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = '../media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    '../static',
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '(u+y!z+=yo+%+!7w&x_$(bgab(elx1c@7yx25wq*w)z*z5xk+!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'core.context_processors.device_info',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'core.middleware.BrowserCheckingMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    'templates',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.comments',
    'django.contrib.sitemaps',

    'grappelli',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    #'django.contrib.admindocs',

    # DannySite specified apps
    'mail',
    'account',

    # Tools
    'ueditor',
    'captcha',
    'widget_tweaks',
    'common',

    # Customed User
    'user',
    'core',
    'dblog',
    'dsite',
    'dshare',
    'dstore',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOG_LEVEL = 'DEBUG'
LOG_FILE_PATH = 'dannysite.log'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(pathname)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE_PATH,
            'maxBytes': 2 * 1024 * 1024,
            'backupCount': 20,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'dannysite': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    }
}

# Grappelli
GRAPPELLI_ADMIN_TITLE = 'DANNYSITE'


# Account Confs
LOGIN_URL = '/account/login/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGIN_REDIRECT_URL = '/'

ACCOUNT_SIGNUP_REDIRECT_URL = '/'

ACCOUNT_OPEN_SIGNUP = False
ACCOUNT_RANDOM_PASSWD_LENGTH = 10
ACCOUNT_LOCK_BY_ATTEMPTED_COUNT = 5
ACCOUNT_LOCK_TIME = 3 * 60 * 60
# Whether email confirmation is required for new signup
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1

# Mail
# Base Confs
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = ''
# EMAIL_PORT = 25
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# EMAIL_USE_TLS = True
# 
# DEFAULT_FROM_EMAIL = ''

# Email Confs
MAX_EMAIL_SENT_COUNT_PERDAY = 5
EMAIL_COUNTER_RESET_INTERVAL = 60 * 60 * 3

EMAIL_PRESENDING_POOL = 'email:presending'
DEFAULT_HTTP_PROTOCOL = 'http'

# Number of threads for sending email
MIN_THREADS_NUM = 1
MAX_THREADS_NUM = 5
THREAD_EXCEPTION_SLEEPTIME = 30
THREAD_SEND_FAILED_SLEEPTIME = 10
MANAGER_EXCEPTION_SLEEPTIME = 60
MANAGER_SCANNING_SLEEPTIME = 30

EMAIL_CONFIRMATION_SUBJECT = u'DannySite账户注册'
EMAIL_CONFIRMATION_MESSAGE = 'mail_confirmation.txt'
EMAIL_CONFIRMATION_HTML = 'mail_confirmation.html'
EMAIL_PASSWD_RESET_SUBJECT = u'DannySite账户密码重置'
EMAIL_PWD_RESET_MSG = 'mail_pwd_reset.txt'
EMAIL_PWD_RESET_HTML = 'mail_pwd_reset.html'
EMAIL_CMT_REPLY_SUBJECT = u'您在DannySite的留言有了新的回复'
EMAIL_CMT_REPLY_MESSAGE = 'mail_reply.txt'
EMAIL_CMT_REPLY_HTML = 'mail_reply.html'

# Blog
BLOG_VISITORS_CACHE_KEY = 'blog:{0}:visitors'
BLOG_VISITORS_CACHE_TIMEOUT = 24 * 60 * 60
BLOG_IMAGE_URL = 'images/uploads/'

# dstore
FILESTORE_ROOT = os.path.abspath('../files/')
FILESTORE_DL_URL = 'http://www.dannysite.com/cloud/dl/'
FILESTORE_DL_NGINX_REDIRECT = '/files/'

# Image
LINK_LOGO_ROOT = 'images/link/'

FOCUS_IMAGE_ROOT = 'images/focus/'
FOCUS_IMAGE_CONF = {
    'limits': {
        'formats': ['.jpg', '.gif', 'jpeg', '.bmp', '.png'],
        'max_file_size': 5 * 1024 * 1024,
        'min_image_size': (280, 280)
    },
    'origin': {
        'dir': os.path.join(FOCUS_IMAGE_ROOT)
    },
    'dims': {
        'normal': {
            'action': 'crop',
            'size': (280, 280),
            'dir': os.path.join(MEDIA_ROOT, FOCUS_IMAGE_ROOT),
            'quality': 100
        }
    }
}

SHARE_IMAGE_ROOT = 'images/share/'
SHARE_IMAGE_CONF = {
    'limits': {
        'formats': ['.jpg', '.gif', 'jpeg', '.bmp', '.png'],
        'max_file_size': 10 * 1024 * 1024,
        'min_image_size': (950, 280)
    },
    'origin': {
        'dir': os.path.join(SHARE_IMAGE_ROOT)
    },
    'dims': {
        'normal': {
            'action': 'scale',
            'size': (950, 0),
            'dir': os.path.join(MEDIA_ROOT, SHARE_IMAGE_ROOT),
            'quality': 100
        }
    }
}

SHARE_UPLOADED_IMAGE_URL = 'images/share/uploads/'
SHARE_UPLOADED_IMAGE_CONF = {
    'limits': {
        'formats': ('.jpg', '.gif', '.jpeg', '.bmp', '.png'),  # 允许上传的文件类型
        'max_file_size': 5 * 1024 * 1024,                      # 上传的文件大小限制
    },
    'origin': {
        'dir': os.path.join(SHARE_IMAGE_ROOT, 'uploads/')
    },
    'dims': {
    },
}

PHOTO_ROOT = 'images/photos/'

PHOTO_CONF = {
    'limits': {
        'formats': ['.jpg', '.gif', 'jpeg', '.bmp', '.png'],
        'max_file_size': 10 * 1024 * 1024,
        'min_image_size': (600, 350)
    },
    'origin': {
        'dir': os.path.join(PHOTO_ROOT, 'original')
    },
    'dims': {
        's950': {
            'action': 'crop',
            'size': (950, 350),
            'dir': os.path.join(MEDIA_ROOT, PHOTO_ROOT, 's950'),
            'quality': 100
        },
        's600': {
            'action': 'crop',
            'size': (600, 350),
            'dir': os.path.join(MEDIA_ROOT, PHOTO_ROOT, 's600'),
            'quality': 100
        },
        's350': {
            'action': 'crop',
            'size': (350, 350),
            'dir': os.path.join(MEDIA_ROOT, PHOTO_ROOT, 's350'),
            'quality': 100
        },
        's200': {
            'action': 'crop',
            'size': (200, 300),
            'dir': os.path.join(MEDIA_ROOT, PHOTO_ROOT, 's200'),
            'quality': 100
        },
        's200c': {
            'action': 'crop',
            'size': (200, 200),
            'dir': os.path.join(MEDIA_ROOT, PHOTO_ROOT, 's200c'),
            'quality': 100
        },
        's175d': {
            'action': 'crop',
            'size': (175, 350),
            'dir': os.path.join(MEDIA_ROOT, PHOTO_ROOT, 's175d'),
            'quality': 100
        },
        's300h': {
            'action': 'crop',
            'size': (300, 350),
            'dir': os.path.join(MEDIA_ROOT, PHOTO_ROOT, 's300h'),
            'quality': 100
        },
        's300l': {
            'action': 'crop',
            'size': (300, 200),
            'dir': os.path.join(MEDIA_ROOT, PHOTO_ROOT, 's300l'),
            'quality': 100
        },
        's300s': {
            'action': 'crop',
            'size': (300, 150),
            'dir': os.path.join(MEDIA_ROOT, PHOTO_ROOT, 's300s'),
            'quality': 100
        },
        's500': {
            'action': 'crop',
            'size': (500, 440),
            'dir': os.path.join(MEDIA_ROOT, PHOTO_ROOT, 's500'),
            'quality': 100
        },
        's250': {
            'action': 'crop',
            'size': (250, 200),
            'dir': os.path.join(MEDIA_ROOT, PHOTO_ROOT, 's250'),
            'quality': 100
        },
        's450': {
            'action': 'crop',
            'size': (450, 240),
            'dir': os.path.join(MEDIA_ROOT, PHOTO_ROOT, 's450'),
            'quality': 100
        }
    }
}

