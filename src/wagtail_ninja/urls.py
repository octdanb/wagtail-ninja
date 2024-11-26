from django.urls import re_path
from .settings import wagtail_ninja_settings
from .router import api

urlpatterns = [
    re_path(r'^/wagtail', api.urls,  name="wagtail_ninja"),
]

