DEBUG = False
THUMBNAIL_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

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
    'pipeline',
    'ckeditor',
    'ckeditor_uploader',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fioulprod',
        'USER': 'fioulprod',
        'PASSWORD': '***',
        'HOST': '***',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX' : 'fioul_prod',
    }
}


FIOUL_MJ_URL = 'https://api.mailjet.com/v3/send'
FIOUL_MJ_USER = 'f0ce962d189483385c8bd795a3215454'
FIOUL_MJ_PASS = '5f80c237d76c0e5173a166923d2c9264'
FIOUL_CONTACT_EMAIL = 'admin@fioulexpress.fr'
FIOUL_ADMIN_EMAIL = 'fioul@m-dev.fr'
FIOUL_CONTACT_NAME = 'Fioul Express'
FIOUL_DEBUG_EMAIL = 'fioulexpress.test@gmail.com'

MONETICO_URL = 'https://p.monetico-services.com/paiement.cgi'
MONETICO_TPE = '6322728'
MONETICO_CLE = '5B0DC68462EE4770386BD18F6A04E31A5F54899E'
MONETICO_SOCIETE = 'fioulexpreIFRAME'

EMAIL_HOST = 'localhost'
ADMINS = [('matthieu', 'matthieu@oax.fr'), ]
SERVER_EMAIL = 'fioul@oax.fr'
