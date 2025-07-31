from django.conf import settings
from django.urls import include, path, re_path
from django.views.defaults import server_error
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from app.api import ninja_api


urlpatterns = [
    path("api/wagtail/v3/", ninja_api.urls),
    path('documents/', include(wagtaildocs_urls)),
    path('admin/', include(wagtailadmin_urls)),
    re_path(r'', include(wagtail_urls)),
]


urlpatterns = [
    *urlpatterns,
    path('404/', TemplateView.as_view(template_name='404.html')),
    path('500/', server_error),
]
