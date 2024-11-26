import os
from .partials.templates import *
from .partials.postgres import *
from .partials.static import *

SECRET_KEY = "supersecretkey"
WAGTAILADMIN_BASE_URL = "https://wagtail-ninja.dev.octave.nz"
DEBUG = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

WAGTAIL_SITE_NAME = 'wagtail-ninja-dev'

ALLOWED_HOSTS = ['wagtail-ninja.dev.octave.nz']
CSRF_TRUSTED_ORIGINS = [ f"https://{host}" for host in ALLOWED_HOSTS]

INSTALLED_APPS = [
    'app',

    'ninja',
    'ninja_extra',
    'wagtail_ninja',

    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',

    'taggit',
    'modelcluster',

    "django.contrib.admin",  # required
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # 'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'app.urls'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Database connection settings:
# https://docs.djangoproject.com/en/4.2/ref/databases/#persistent-connections
CONN_MAX_AGE = 0
# If you override CONN_MAX_AGE, make sure to copy or override this too
CONN_HEALTH_CHECKS = CONN_MAX_AGE is None or CONN_MAX_AGE > 0
