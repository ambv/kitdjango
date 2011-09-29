# Django settings for dummy project.
from lck.django import current_dir_support
execfile(current_dir_support)

from lck.django import namespace_package_support
execfile(namespace_package_support)

#
# common stuff for each install
#

ADMINS = (
    ('Lukasz Langa', 'lukasz@langa.pl'),
)
MANAGERS = ADMINS
DEFAULT_FROM_EMAIL = 'lukasz@langa.pl'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
TIME_ZONE = 'Europe/Warsaw'
LANGUAGE_CODE = 'pl-pl'
SITE_ID = 1
USE_I18N = True
USE_L10N = True #FIXME: breaks contents of localized date fields on form reload
MEDIA_ROOT = CURRENT_DIR + 'uploads'
MEDIA_URL = '/uploads/'
STATIC_ROOT = CURRENT_DIR + 'static'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
FILE_UPLOAD_TEMP_DIR = CURRENT_DIR + 'uploads-part'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'lck.django.common.middleware.TimingMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'lck.django.common.middleware.ActivityMiddleware',
    'lck.django.common.middleware.AdminForceLanguageCodeMiddleware',
)
ROOT_URLCONF = 'dummy.urls'
TEMPLATE_DIRS = (CURRENT_DIR + "templates",)
LOCALE_PATHS = (CURRENT_DIR + "locale",)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.comments',
    'django.contrib.flatpages',
    #'django_crystal_small',
    #'django_crystal_big',
    #'django_evolution',
    #'django_extensions',
    #'gunicorn',
    #'haystack',
    'lck.django.common',
    'lck.django.activitylog',
    'lck.django.profile',
    'lck.django.score',
    'lck.django.tags',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
)
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
FORCE_SCRIPT_NAME = ''
# django.contrib.auth settings
AUTH_PROFILE_MODULE = 'defaults.Profile'
# LOGIN_REDIRECT_URL = '/pl/'
# LOGIN_URL = '/pl/auth/login/'
# LOGOUT_URL = '/pl/auth/logout/'
# django.contrib.messages settings
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
# django-staticfiles settings
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'lck.django.staticfiles.LegacyAppDirectoriesFinder',
)
STATICFILES_DIRS = (
    CURRENT_DIR + 'media',
)
# activity middleware settings
CURRENTLY_ONLINE_INTERVAL = 300
RECENTLY_ONLINE_INTERVAL = 900

# lck.django.common models
EDITOR_TRACKABLE_MODEL = "defaults.Profile"
DEFAULT_SAVE_PRIORITY = 0

# lck.django.score models
SCORE_VOTER_MODEL = "defaults.Profile"
# lck.django.tags models
TAG_AUTHOR_MODEL = "defaults.Profile"

#
# stuff that should be customized in settings_local.py
#
SECRET_KEY = 'u*pk)&+kxuyj+rgb&z%!*c4$drco@zs=pob3ugey0#fa@m@c4w'
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DUMMY_SEND_MAIL = DEBUG
SEND_BROKEN_LINK_EMAILS = DEBUG
DATABASES = dict(
    default = dict(
        ENGINE = 'django.db.backends.sqlite3',
        NAME = TEMP_DIR + 'development.db', # XXX: Please note the TEMP_DIR
        USER = '',
        PASSWORD = '',
        HOST = '',
        PORT = '',
        OPTIONS = dict(
            timeout = 30,
        )
    )
)
CACHES = dict(
    default = dict(
        BACKEND = 'django.core.cache.backends.memcached.MemcachedCache',
        #BACKEND = 'django.core.cache.backends.memcached.PyLibMCCache',
        LOCATION = '127.0.0.1:11211',
        TIMEOUT = 300,
        OPTIONS = dict(
            CULL_FREQUENCY = 0,
        ),
        KEY_PREFIX = 'dummy_',
    )
)
INTERNAL_IPS = ['127.0.0.1', '::1', 'localhost']


from lck.django import profile_support
execfile(profile_support)
