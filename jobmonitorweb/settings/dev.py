from .base import *  # NOQA

DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

try:
    import debug_toolbar  # NOQA
    INSTALLED_APPS += ('debug_toolbar',)  # NOQA
    MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)  # NOQA
    INTERNAL_IPS = ('127.0.0.1',)
except ImportError:
    pass
