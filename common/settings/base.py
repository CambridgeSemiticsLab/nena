"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = environ.Path(__file__) - 3
WEBROOT_DIR = environ.Path(__file__) - 4

env = environ.Env()

READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=True)
if READ_DOT_ENV_FILE:
    env_file = str(BASE_DIR.path('.env'))
    print('Loading : {}'.format(env_file))
    env.read_env(env_file)
    print('The .env file has been loaded. See base.py for more information')


DEBUG    = env.bool('DJANGO_DEBUG', False)
SECRET_KEY = env('DJANGO_SECRET_KEY')


ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS', default='').split(',')

# Application definition

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'treebeard',
    'imagekit',
    'ucamprojectlight',
    'ucamwebauth',
    'storages',
    'widget_tweaks',
    'django_github_push_deploy',
)

LOCAL_APPS = (
    'common',
    'dialects',
    'grammar',
    'dialectmaps',
    'audio',
    'gallery',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTHENTICATION_BACKENDS = (
    'ucamwebauth.backends.RavenAuthBackend',
    'django.contrib.auth.backends.ModelBackend'
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'common.urls'

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
                'common.context_processors.google_analytics_reference',
                'common.context_processors.last_updated_date',
            ],
        },
    },
]

WSGI_APPLICATION = 'common.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DJANGO_DB_DEFAULT_NAME'),
        'USER': env('DJANGO_DB_DEFAULT_USER'),
        'PASSWORD': env('DJANGO_DB_DEFAULT_PASSWORD'),
        'HOST': env('DJANGO_DB_HOST', default='localhost'),
        'PORT': env('DJANGO_DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': 'SET default_storage_engine=INNODB;',
            'sql_mode': 'STRICT_TRANS_TABLES',
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

GS_PROJECT_ID = env('GS_PROJECT_ID', default=None) # Set in .env if we're using Google Storage for site assets
if GS_PROJECT_ID: # Files are stored and served from a bucket in Google Cloud Storage
    DEFAULT_FILE_STORAGE = 'common.storage_backends.GoogleCloudMediaStorage'
    STATICFILES_STORAGE = 'common.storage_backends.GoogleCloudStaticStorage'
    GS_BUCKET_NAME = env('GS_BUCKET_NAME')
    GS_STATIC_BUCKET_NAME = GS_BUCKET_NAME
    GS_MEDIA_BUCKET_NAME = GS_BUCKET_NAME
    STATIC_URL = 'https://storage.googleapis.com/{}/'.format(GS_STATIC_BUCKET_NAME)
    MEDIA_URL = 'https://storage.googleapis.com/{}/'.format(GS_MEDIA_BUCKET_NAME)
else: # Files are stored and served locally
    STATIC_ROOT = str(BASE_DIR.path('static'))
    STATIC_URL = '/static/'
    MEDIA_ROOT = str(BASE_DIR.path('media'))
    MEDIA_URL = '/media/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# django_github_push_deploy settings
GITHUB_DEPLOY_KEY  = env('GITHUB_DEPLOY_KEY', default='')
DEPLOY_COMMAND     = env('DEPLOY_COMMAND', default='')

LAST_UPDATED_DATE = env('DJANGO_LAST_UPDATED_DATE', default='')
GOOGLE_ANALYTICS_REFERENCE = env('DJANGO_GOOGLE_ANALYTICS_REFERENCE', default=None)
