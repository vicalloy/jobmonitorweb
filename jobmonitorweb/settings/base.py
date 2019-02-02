"""
Django settings for jobmonitorweb project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

from lbjobmonitor.message import CLIMessageBackend
from lbjobmonitor.message import FileMessageBackend
from lbjobmonitor.message import SlackMessageBackend

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, 'datas')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+6cfll)e(5b@jwkyh04nqt#b(4#i#fey*2@bqd89l!vf(sl!&q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'channels',
    'django_celery_results',
    'stronghold',

    'jobmonitorweb',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jobmonitorweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'jobmonitorweb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = '/admin/login/'

STRONGHOLD_PUBLIC_URLS = (LOGIN_URL, )


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

ASGI_APPLICATION = "jobmonitorweb.routing.application"

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # our redis address
CELERY_BROKER_TRANSPORT = 'redis'
# use json format for everything
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'

# message_backend_factory


def message_backend_factory(backend_type, monitor, **kwargs):
    from jobmonitorweb.messagebackends import WSMessageBackend
    from jobmonitorweb.messagebackends import DbMessageBackend

    if backend_type == 'cli':
        return CLIMessageBackend()
    elif backend_type == 'slack':
        # v2ex don't send job counts
        slack_api_key = ''
        slack_channel = ''
        show_jobs_count = True
        return SlackMessageBackend(
            slack_api_key,
            slack_channel,
            show_jobs_count=show_jobs_count
        )
    elif backend_type == 'ws':
        channel_layer = kwargs.get('channel_layer')
        group_name = kwargs.get('group_name')
        return WSMessageBackend(
            channel_layer=channel_layer,
            group_name=group_name,
            monitor=monitor
        )
    elif backend_type == 'db':
        return DbMessageBackend(monitor=monitor, with_separtor=False)
    elif backend_type == 'file':
        fn = os.path.join(DATA_DIR, '%s-%s.json' % (monitor.monitor_class.value, monitor.pk))
        return FileMessageBackend(fn=fn)
    return None


JM_MESSAGE_BACKEND_FACTORY = message_backend_factory
