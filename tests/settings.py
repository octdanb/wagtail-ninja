import contextlib
import pathlib

import dj_database_url

from wagtail import VERSION as WAGTAIL_VERSION


BASE_DIR = pathlib.Path(__file__).parents[0]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    "testapp",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "wagtail.contrib.settings",
    "modelcluster",
    "wagtailmedia",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "wagtail_headless_preview",
    # WAGTAIL_NINJA SPECIFIC MODULES
    "wagtail_ninjaninja",
    "ninja_extra",
    "wagtail_ninja"
]

if WAGTAIL_VERSION >= (6, 0):
    INSTALLED_APPS.append("wagtail.contrib.search_promotions")

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
]

MIDDLEWARE += ["wagtail.contrib.redirects.middleware.RedirectMiddleware"]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "testapp" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# Javascript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/4.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "/static/"

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"


# Wagtail settings

WAGTAIL_SITE_NAME = "Grapple example"
WAGTAILIMAGES_IMAGE_MODEL = "testapp.CustomImage"
WAGTAILIMAGES_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp", "svg"]

WAGTAILDOCS_DOCUMENT_MODEL = "testapp.CustomDocument"
WAGTAILDOCS_SERVE_METHOD = "serve_view"

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
# BASE_URL is removed as of WAGTAIL 3.0, remove once WAGTAIL 2.0 is no longer supported
BASE_URL = "http://localhost:8000"
# as of Wagtail 3.0 BASE_URL was renamed to WAGTAILADMIN_BASE_URL, both are provided here for compatibility
# when testing with Wagtail 2.0
WAGTAILADMIN_BASE_URL = "http://localhost:8000"

CORS_ORIGIN_ALLOW_ALL = True

# Grapple Config:
GRAPHENE = {
    "SCHEMA": "wagtail_ninja.schema.schema",
    "MIDDLEWARE": ["wagtail_ninja.middleware.GrappleMiddleware"],
}

# WAGTAIL_NINJA_EXPOSE_GRAPHIQL = True

WAGTAIL_NINJA = {
    "APPS": ["testapp"],
    "ADD_SEARCH_HIT": True,
    "EXPOSE_GRAPHIQL": True,
}

WAGTAIL_HEADLESS_PREVIEW = {"CLIENT_URLS": {"default": "http://localhost:8001/preview"}}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DEBUG = True

SECRET_KEY = "this-is-not-a-secret"  # noqa: S105

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


with contextlib.suppress(ImportError):
    from .local import *  # noqa: F403
