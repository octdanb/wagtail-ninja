DJANGO_DATABASE_NAME = 'wagtail_ninja'
DJANGO_DATABASE_USER = 'wagtail_ninja'
DJANGO_DATABASE_PASSWORD = 'wagtail_ninja'
DJANGO_DATABASE_HOST = 'wagtail-ninja-postgres'
DJANGO_DATABASE_PORT = 5432

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DJANGO_DATABASE_NAME,
        "USER": DJANGO_DATABASE_USER,
        "PASSWORD": DJANGO_DATABASE_PASSWORD,
        "HOST": DJANGO_DATABASE_HOST,
        "PORT": DJANGO_DATABASE_PORT,
        "OPTIONS": {
            "application_name": "sbs-wealth-web-app_django",
        }
    }
}
