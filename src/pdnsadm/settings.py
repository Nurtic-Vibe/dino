"""
Django settings for pdnsadm project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import distutils.util
import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def env(name, default='__unset', kind=str):
    env_name = f'PDNSADM_{name.upper()}'

    try:
        value = os.environ[env_name]
    except LookupError:
        if default != '__unset':
            return default
        else:
            raise ImproperlyConfigured(f'Environment variable ${env_name} is not set.')

    if kind == str:
        return value
    elif kind == list:
        return value.split(',')
    elif kind == bool:
        return distutils.util.strtobool(value)
    else:
        raise Exception(f'Invalid variable type {kind} for {name}/{env_name}.')


SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG', False, bool)
ALLOWED_HOSTS = env('ALLOWED_HOSTS', [], list)
PDNS_APIURL = env('PDNS_APIURL')
PDNS_APIKEY = env('PDNS_APIKEY')

# Application definition

INSTALLED_APPS = [
    # disable django development static file handler
    'whitenoise.runserver_nostatic',

    # core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # 1st party
    'pdnsadm.common',
    'pdnsadm.zoneeditor',
    'pdnsadm.synczones',
    'pdnsadm.tenants',

    # 3rd party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rules.apps.AutodiscoverRulesConfig',
]

if DEBUG:
    INSTALLED_APPS += ['django_extensions']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pdnsadm.urls'

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

WSGI_APPLICATION = 'pdnsadm.wsgi.application'

# Authentication
# https://docs.djangoproject.com/en/2.1/topics/auth/
# https://django-allauth.readthedocs.io/en/latest/

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1
ACCOUNT_ADAPTER = 'pdnsadm.common.allauth.NoNewUsersAccountAdapter'
LOGIN_REDIRECT_URL = '/'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

default_db_url = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
DATABASES = {
    'default': dj_database_url.config(default=env('DB_URL', default_db_url), conn_max_age=600),
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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Logging
# https://docs.djangoproject.com/en/2.1/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'rules': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# Custom Settings
ENABLE_SIGNUP = env('ENABLE_SIGNUP', False, kind=bool)
# may be 'Native', 'Master' or 'Slave'
# see https://doc.powerdns.com/authoritative/http-api/zone.html#zone
ZONE_DEFAULT_KIND = env('ZONE_DEFAULT_KIND', 'Native', kind=bool)
ZONE_DEFAULT_NAMESERVERS = env('ZONE_DEFAULT_NAMESERVERS', [], kind=list)

if env('USE_DEFAULT_RECORD_TYPES', True, kind=bool):
    RECORD_TYPES = [
        'A', 'AAAA', 'AFSDB', 'ALIAS', 'CAA', 'CERT', 'CDNSKEY','CDS',
        'CNAME', 'DNAME', 'DS', 'KEY', 'LOC', 'MX', 'NAPTR',
        'NS', 'OPENPGPKEY', 'PTR', 'RP', 'SOA', 'SSHFP', 'SRV',
        'TKEY', 'TSIG', 'TLSA', 'SMIMEA', 'TXT', 'URI',
    ]
else:
    RECORD_TYPES = []

RECORD_TYPES = RECORD_TYPES + env('CUSTOM_RECORD_TYPES', [], kind=list)
RECORD_TYPES = [(t, t) for t in RECORD_TYPES]
