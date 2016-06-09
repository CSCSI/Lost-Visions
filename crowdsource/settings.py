"""
Django settings for crowdsource project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8_999634*12p^3tbhm=t^f$3*$+xg+_h*w@+_r!93vy-j(g#cy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

SITE_ID = 3

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = ''
EMAIL_PORT = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

# Application definition

INSTALLED_APPS = (
    # 'admin_tools',
    # 'admin_tools.theming',
    # 'admin_tools.menu',
    # 'admin_tools.dashboard',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    # 'django.contrib.gis',
    # 'social.apps.django_app.default',
    # 'dajaxice',
    # 'dajax',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.facebook',
    # 'allauth.socialaccount.providers.twitter',

    'raven.contrib.django.raven_compat',

    'haystack',
    # 'watson',
    'lost_visions',
    'reimagine'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    "allauth.account.auth_backends.AuthenticationBackend"
)

ROOT_URLCONF = 'crowdsource.urls'

WSGI_APPLICATION = 'crowdsource.wsgi.application'

# Templates, mostly for dajax

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'lost_visions/templates'),
    os.path.join(BASE_DIR, 'reimagine/templates')
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',

    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
)

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True

LOGIN_REDIRECT_URL = '/'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': ['email', 'publish_stream'],
        'METHOD': 'js_sdk'  # instead of 'oauth2'
    }
}

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

#ATOMIC_REQUESTS used to stop horrible memory hogging idle transactions
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ATOMIC_REQUESTS': True
        },
    'wordnet': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'sqlite-31.db'),
        },
    #postgres
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'local_db',
    #     'USER': 'local_user',
    #     'PASSWORD': 'l0c4l111',
    #     'HOST': 'localhost'
    # },
    # 'geodjango': {
    #      'ENGINE': 'django.contrib.gis.db.backends.postgis',
    #      'NAME': 'geodjango',
    #      'USER': 'geo',
    #  }
}

# DATABASE_ROUTERS = ['lost_visions.MarioRouter.MarioRouter']

# POSTGIS_VERSION = ( 1.5, )

# RAVEN_CONFIG = {
#     'dsn': 'http://8eedfb9d1deb48a39af1f63b825e4ccc:e0f83797e67a462c9c65f270296e672c@lost-visions.cf.ac.uk/sentry/2',
# }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = '/lost_visions/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'dajaxice.finders.DajaxiceFinder',

    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            },
        },
    'loggers': {
        'lost_visions': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
            },
        },
    }

bl_folder = ''
db_json_location = ''
db_cleaned_json_location = ''

recorded_image_root = '/scratch/lost-visions/images-found/'
web_server_start_resized = '/static/media/images/resized/'
web_server_start = '/static/media/images/scans/'

bl_image_root = '/lost-visions/images-found/'
resized_start = '/lost-visions/resized/lost-visions/images-found/'

#\b for sqlite \y for postgres
db_regex_char = "\\b"

thumbnail_size = 300
use_flickr = False
shrink_arcca_images = False
find_arcca_thumbnail = True
use_azure = False

TRUSTED_COLLECTIONS = []

kismet_api_key = ''

captcha_secret = ''

MAX_RESULTS = 10000
# Solr limits number of boolean searches
MAX_BOOK_RESULTS = 10000

try:
    from crowdsource.settings_local import *
except ImportError:
    pass