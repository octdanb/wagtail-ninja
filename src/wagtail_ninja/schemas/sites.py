from __future__ import annotations

from typing import Optional, List

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page as WagtailPage
from wagtail.models import Site

from ..utils import resolve_queryset, resolve_site_by_hostname, resolve_site_by_id
from .interfaces import get_page_interface
from .pages import get_specific_page
from .structures import QuerySetList
from .base import BaseSchema

class SiteObjectType(BaseSchema):
    pages: List[get_page_interface()] = []
    page: get_page_interface() = None

    def resolve_pages(self, info, **kwargs):
        pages = WagtailPage.objects.in_site(self).live().public().specific()

        content_type = kwargs.pop("content_type", None)
        if content_type:
            app_label, model = content_type.strip().lower().split(".")
            try:
                ctype = ContentType.objects.get(app_label=app_label, model=model)
            except ContentType.DoesNotExist:
                return (
                    WagtailPage.objects.none()
                )  # something not quite right here, bail out early
            else:
                pages = pages.filter(content_type=ctype)

        return resolve_queryset(pages, info, **kwargs)

    def resolve_page(self, info, **kwargs):
        return get_specific_page(
            id=kwargs.get("id"),
            slug=kwargs.get("slug"),
            url_path=kwargs.get("url_path"),
            token=kwargs.get("token"),
            content_type=kwargs.get("content_type"),
            site=self,
        )

    class Meta:
        model = Site


def SitesQuery():
    class Mixin:
        site = graphene.Field(
            SiteObjectType, hostname=graphene.String(), id=graphene.ID()
        )
        sites = QuerySetList(
            graphene.NonNull(SiteObjectType), enable_search=True, required=True
        )

        def resolve_sites(self, info, **kwargs) -> QuerySet[Site]:
            """
            Return all `Site` objects.
            """

            return resolve_queryset(Site.objects.all(), info, **kwargs)

        def resolve_site(self, info, **kwargs) -> Optional[Site]:
            """
            Attempt to return a single `Site` object identified by ID or
            hostname.
            """

            if id := kwargs.get("id"):
                return resolve_site_by_id(id=id)
            elif hostname := kwargs.get("hostname"):
                return resolve_site_by_hostname(
                    hostname=hostname,
                    filter_name="hostname",
                )
            return None

    return Mixin