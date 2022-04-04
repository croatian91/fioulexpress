import os


DEBUG = False
THUMBNAIL_DEBUG = DEBUG

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "dal",
    "dal_select2",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "fioulexpress",
    "import_export",
    "contenu",
    "sorl.thumbnail",
    "markdownx",
    "pipeline",
    "ckeditor",
    "ckeditor_uploader",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "fioulprod",
        "USER": "fioulprod",
        "PASSWORD": "***",
        "HOST": "***",
        "PORT": "5432",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
        "KEY_PREFIX": "fioul_prod",
    }
}


FIOUL_MJ_URL = os.getenv("FIOUL_MJ_URL", "https://api.mailjet.com/v3/send")
FIOUL_MJ_USER = os.getenv("FIOUL_MJ_USER")
FIOUL_MJ_PASS = os.getenv("FIOUL_MJ_PASS")
FIOUL_CONTACT_EMAIL = os.getenv("FIOUL_CONTACT_EMAIL", "admin@fioulexpress.fr")
FIOUL_ADMIN_EMAIL = os.getenv("FIOUL_ADMIN_EMAIL", "fioul@m-dev.fr")
FIOUL_CONTACT_NAME = os.getenv("FIOUL_CONTACT_NAME", "Fioul Express")
FIOUL_DEBUG_EMAIL = os.getenv("FIOUL_DEBUG_EMAIL", "fioulexpress.test@gmail.com")

MONETICO_URL = os.getenv("MONETICO_URL", "https://p.monetico-services.com/paiement.cgi")
MONETICO_TPE = os.getenv("MONETICO_TPE")
MONETICO_CLE = os.getenv("MONETICO_CLE")
MONETICO_SOCIETE = os.getenv("MONETICO_SOCIETE")

EMAIL_HOST = "localhost"
ADMINS = [
    ("matthieu", "matthieu@oax.fr"),
]
SERVER_EMAIL = "fioul@oax.fr"
