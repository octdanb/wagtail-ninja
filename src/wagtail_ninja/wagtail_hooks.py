from django.apps import apps
from wagtail import hooks

from .registry import registry
from .schemas.base import BaseSchema
# from .schemas.collections import CollectionsQuery
# from .schemas.documents import DocumentsQuery
# from .schemas.images import ImagesQuery
from .schemas.pages import PagesQuery
# from .schemas.redirects import RedirectsQuery
# from .schemas.search import SearchQuery
# from .schemas.settings import SettingsQuery
from .schemas.sites import SitesQuery
# from .schemas.snippets import SnippetsQuery
# from .schemas.tags import TagsQuery

@hooks.register("register_schema_query")
def register_schema_query(query_mixins):
    query_mixins += [
        BaseSchema,
        PagesQuery(),
        SitesQuery(),
        # ImagesQuery(),
        # DocumentsQuery(),
        # SnippetsQuery(),
        # SettingsQuery(),
        # SearchQuery(),
        # TagsQuery(),
        # CollectionsQuery(),
        # RedirectsQuery,
    ]

    # if apps.is_installed("wagtailmedia"):
    #     from .schemas.media import MediaQuery
    #
    #     query_mixins.append(MediaQuery())

    query_mixins += registry.schema
