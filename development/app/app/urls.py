from django.conf import settings
from django.urls import include, path, re_path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from wagtail_ninja.router import api


urlpatterns = [
    re_path(r'^api/v1/', api.urls),
    path('documents/', include(wagtaildocs_urls)),
    path('admin/', include(wagtailadmin_urls)),
    re_path(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.views.defaults import server_error
    from django.views.generic import TemplateView

    urlpatterns = [
        *urlpatterns,
        path('404/', TemplateView.as_view(template_name='404.html')),
        path('500/', server_error),
    ]
