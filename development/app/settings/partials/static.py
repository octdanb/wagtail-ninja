# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
import os
from .paths import PROJECT_DIR, BASE_DIR

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# needed to ensure that media/images have the right permissions applied upon upload
# particularly needed for larger files that are uploaded via intermediate temp directories
# this also gets used by the `collectstatic` command to set file permissions when run.
FILE_UPLOAD_PERMISSIONS = 0o766
