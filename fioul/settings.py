"""
Django settings for fioul project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

import django_on_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", False)
THUMBNAIL_DEBUG = os.getenv("THUMBNAIL_DEBUG", False)

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fioulexpress',
    'import_export',
    'contenu',
    'sorl.thumbnail',
    'markdownx',
    'ckeditor',
    'ckeditor_uploader',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fioul.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates', ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'fioulexpress.context_processors.config_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'fioul.wsgi.application'


# Dev database settings, no password, to be overridden by prod settings
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
SESSION_COOKIE_AGE = 3600
# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_HOST = 's3.eu-west-3.amazonaws.com'
AWS_S3_REGION_NAME = 'eu-west-3'
S3_USE_SIGV4 = True
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", None)
AWS_STATIC_URL = "https://{}/{}".format(AWS_S3_HOST, AWS_STORAGE_BUCKET_NAME)
AWS_DEFAULT_ACL = None

STATICFILES_DIRS = ["root"]
STATIC_URL = '/static/'
STATIC_ROOT = os.getenv("{}/static/".format(AWS_STATIC_URL), None)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.getenv("{}/media/".format(AWS_STATIC_URL), None)

# THUMBNAIL_HIGH_RESOLUTION = True

CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_UPLOAD_PATH = 'media/ck/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_BROWSE_SHOW_DIRS = True

# Email settings
FIOUL_MJ_URL = 'https://api.mailjet.com/v3/send'
FIOUL_MJ_USER = 'f0ce962d189483385c8bd795a3215454'
FIOUL_MJ_PASS = '5f80c237d76c0e5173a166923d2c9264'
FIOUL_CONTACT_EMAIL = 'admin@fioulexpress.fr'
FIOUL_ADMIN_EMAIL = 'fioul@m-dev.fr'
FIOUL_CONTACT_NAME = 'Fioul Express'
FIOUL_DEBUG_EMAIL = 'fioulexpress.test@gmail.com'

# Monetico payment settings
MONETICO_URL = 'https://p.monetico-services.com/paiement.cgi'
MONETICO_TPE = '6322728'
MONETICO_CLE = '5B0DC68462EE4770386BD18F6A04E31A5F54899E'
MONETICO_SOCIETE = 'fioulexpreIFRAME'

# Activate Django-Heroku.
django_on_heroku.settings(locals())

# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'fioul.storage_backends.StaticStorage'
DEFAULT_FILE_STORAGE = 'fioul.storage_backends.PublicMediaStorage'
