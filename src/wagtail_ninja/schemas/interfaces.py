from __future__ import annotations

import inspect
from typing import Union
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.utils.module_loading import import_string
from wagtail import blocks
from wagtail.models import Page as WagtailPage
from wagtail.rich_text import RichText

from .base import BaseSchema
from ..registry import registry
from ..settings import wagtail_ninja_settings
from ..utils import resolve_queryset, serialize_struct_obj
from .structures import QuerySetList


def get_page_interface():
    return import_string(wagtail_ninja_settings.PAGE_INTERFACE)


class PageInterface(BaseSchema):
    id: Union[int, None] = None
    title: str
    slug: str
    content_type: str
    page_type: str
    live: bool

    url: Union[str, None] = None
    url_path: str

    depth: int
    seo_title: str
    search_description: Union[str, None] = None
    show_in_menus: bool

    locked: Union[bool, None] = None

    first_published_at: datetime
    last_published_at: datetime

    parent: PageInterface = None
    children:  List[PageInterface] = []
    # QuerySetList(
    #     PageInterface,
    #     enable_search=True,
    #     required=True,
    #     enable_in_menu=True,
    # )
    siblings: List[PageInterface] = []
    # QuerySetList(
    #     PageInterface,
    #     enable_search=True,
    #     required=True,
    #     enable_in_menu=True,
    # )
    next_siblings: List[PageInterface] = []
    # QuerySetList(
    #     PageInterface,
    #     enable_search=True,
    #     required=True,
    #     enable_in_menu=True,
    # )
    previous_siblings: List[PageInterface] = []
    # QuerySetList(
    #     PageInterface,
    #     enable_search=True,
    #     required=True,
    #     enable_in_menu=True,
    # )
    descendants: List[PageInterface] = []
    #     PageInterface,
    #     enable_search=True,
    #     required=True,
    #     enable_in_menu=True,
    # )
    ancestors: List[PageInterface] = []

    # parent: lambda: get_page_interface()
    # children: QuerySetList(
    #     lambda: get_page_interface(),
    #     enable_search=True,
    #     required=True,
    #     enable_in_menu=True,
    # )
    # siblings: QuerySetList(
    #     lambda: get_page_interface(),
    #     enable_search=True,
    #     required=True,
    #     enable_in_menu=True,
    # )
    # next_siblings: QuerySetList(
    #     lambda: get_page_interface(),
    #     enable_search=True,
    #     required=True,
    #     enable_in_menu=True,
    # )
    # previous_siblings: QuerySetList(
    #     lambda: get_page_interface(),
    #     enable_search=True,
    #     required=True,
    #     enable_in_menu=True,
    # )
    # descendants: QuerySetList(
    #     lambda: get_page_interface(),
    #     enable_search=True,
    #     required=True,
    #     enable_in_menu=True,
    # )
    # ancestors: QuerySetList(
    #     lambda: get_page_interface(),
    #     enable_search=True,
    #     required=True,
    #     enable_in_menu=True,
    # )

    search_score: float = 0

    @classmethod
    def resolve_type(cls, instance, info, **kwargs):
        """
        If model has a custom WagtailNinjaSchema Node type in registry then use it,
        otherwise use base page type.
        """
        from .pages import PageSchema

        return registry.pages.get(type(instance), PageSchema)

    def resolve_content_type(self, info, **kwargs):
        self.content_type = ContentType.objects.get_for_model(self)
        return (
            f"{self.content_type.app_label}.{self.content_type.model_class().__name__}"
        )

    def resolve_page_type(self, info, **kwargs):
        return get_page_interface().resolve_type(self.specific, info, **kwargs)

    def resolve_parent(self, info, **kwargs):
        """
        Resolves the parent node of current page node.
        Docs: https://docs.wagtail.io/en/stable/reference/pages/model_reference.html#wagtail.models.Page.get_parent
        """
        try:
            return self.get_parent().specific
        except:
            return WagtailPage.objects.none()

    def resolve_children(self, info, **kwargs):
        """
        Resolves a list of live children of this page.
        Docs: https://docs.wagtail.io/en/stable/reference/pages/queryset_reference.html#examples
        """
        return resolve_queryset(
            self.get_children().live().public().specific(), info, **kwargs
        )

    def resolve_siblings(self, info, **kwargs):
        """
        Resolves a list of sibling nodes to this page.
        Docs: https://docs.wagtail.io/en/stable/reference/pages/queryset_reference.html?highlight=get_siblings#wagtail.query.PageQuerySet.sibling_of
        """
        return resolve_queryset(
            self.get_siblings().exclude(pk=self.pk).live().public().specific(),
            info,
            **kwargs,
        )

    def resolve_next_siblings(self, info, **kwargs):
        """
        Resolves a list of direct next siblings of this page. Similar to `resolve_siblings` with sorting.
        Source: https://github.com/wagtail/wagtail/blob/master/wagtail/core/models.py#L1384
        """
        return resolve_queryset(
            self.get_next_siblings().exclude(pk=self.pk).live().public().specific(),
            info,
            **kwargs,
        )

    def resolve_previous_siblings(self, info, **kwargs):
        """
        Resolves a list of direct prev siblings of this page. Similar to `resolve_siblings` with sorting.
        Source: https://github.com/wagtail/wagtail/blob/master/wagtail/core/models.py#L1387
        """
        return resolve_queryset(
            self.get_prev_siblings().exclude(pk=self.pk).live().public().specific(),
            info,
            **kwargs,
        )

    def resolve_descendants(self, info, **kwargs):
        """
        Resolves a list of nodes pointing to the current page’s descendants.
        Docs: https://docs.wagtail.io/en/stable/reference/pages/model_reference.html#wagtail.models.Page.get_descendants
        """
        return resolve_queryset(
            self.get_descendants().live().public().specific(), info, **kwargs
        )

    def resolve_ancestors(self, info, **kwargs):
        """
        Resolves a list of nodes pointing to the current page’s ancestors.
        Docs: https://docs.wagtail.io/en/stable/reference/pages/model_reference.html#wagtail.models.Page.get_ancestors
        """
        return resolve_queryset(
            self.get_ancestors().live().public().specific(), info, **kwargs
        )

    def resolve_seo_title(self, info, **kwargs):
        """
        Get page's SEO title. Fallback to a normal page's title if absent.
        """
        return self.seo_title or self.title

    def resolve_search_score(self, info, **kwargs):
        """
        Get page's search score, will be None if not in a search context.
        """
        return getattr(self, "search_score", None)


class StreamFieldInterface(BaseSchema):
    id: str = None
    block_type: str = None
    field: str = None
    raw_value: str = None
    #
    # @staticmethod
    # def resolve_type(instance):
    #     """
    #     If block has a custom Graphene Node type in registry then use it,
    #     otherwise use generic block type.
    #     """
    #     if hasattr(instance, "block"):
    #         mdl = type(instance.block)
    #         if mdl in registry.streamfield_blocks:
    #             return registry.streamfield_blocks[mdl]
    #
    #         for block_class in inspect.getmro(mdl):
    #             if block_class in registry.streamfield_blocks:
    #                 return registry.streamfield_blocks[block_class]
    #     return registry.streamfield_blocks["generic-block"]
    #
    # @staticmethod
    # def resolve_id(instance, **kwargs):
    #     return instance.id
    #
    # @staticmethod
    # def resolve_block_type(instance, **kwargs):
    #     return type(instance.block).__name__
    #
    # @staticmethod
    # def resolve_field(instance, **kwargs):
    #     return instance.block.name
    #
    # @staticmethod
    # def resolve_raw_value(instance, **kwargs):
    #     if isinstance(instance, blocks.StructValue):
    #         # This is the value for a nested StructBlock defined via GraphQLStreamfield
    #         return serialize_struct_obj(instance)
    #     elif isinstance(instance.value, dict):
    #         return serialize_struct_obj(instance.value)
    #     elif isinstance(instance.value, RichText):
    #         # Ensure RichTextBlock raw value always returns the "internal format", rather than the conterted value
    #         # as per https://docs.wagtail.io/en/stable/extending/rich_text_internals.html#data-format.
    #         # Note that RichTextBlock.value will be rendered HTML by default.
    #         return instance.value.source
    #
    #     return instance.value


def get_snippet_interface():
    return import_string(wagtail_ninja_settings.SNIPPET_INTERFACE)


class SnippetInterface(BaseSchema):
    snippet_type: str
    content_type: str

    # @classmethod
    # def resolve_type(cls, instance, info, **kwargs):
    #     return registry.snippets[type(instance)]
    #
    # def resolve_snippet_type(self, info, **kwargs):
    #     return self.__class__.__name__
    #
    # def resolve_content_type(self, info, **kwargs):
    #     self.content_type = ContentType.objects.get_for_model(self)
    #     return (
    #         f"{self.content_type.app_label}.{self.content_type.model_class().__name__}"
    #     )
