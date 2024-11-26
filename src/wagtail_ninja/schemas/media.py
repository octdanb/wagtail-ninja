from wagtailmedia.models import Media, get_media_model

from ..registry import registry
from ..utils import get_media_item_url, resolve_queryset
from .collections import CollectionObjectSchema
from .structures import QuerySetList
from .base import BaseSchema


class MediaObjectType(BaseSchema):
    class Meta:
        model = Media
        exclude = ("tags",)

    url: str
    collection: CollectionObjectSchema

    def resolve_url(self, info, **kwargs):
        """
        Get Media file url.
        """
        return get_media_item_url(self)


def MediaQuery():
    registry.media[Media] = MediaObjectType
    mdl = get_media_model()
    mdl_type = get_media_type()

    class Mixin:
        media_item: int
        media: QuerySetList(mdl_type, enable_search=True, required=True)

        def resolve_media_item(self, info, id, **kwargs):
            """Returns a media item given the id, if in a public collection"""
            try:
                return mdl.objects.filter(
                    collection__view_restrictions__isnull=True
                ).get(pk=id)
            except mdl.DoesNotExist:
                return None

        def resolve_media(self, info, **kwargs):
            """Return only the items with no collection or in a public collection"""
            qs = mdl.objects.filter(collection__view_restrictions__isnull=True)
            return resolve_queryset(qs, info, **kwargs)

        def resolve_media_type(self, info, **kwargs):
            return mdl_type

    return Mixin


def get_media_type():
    registry.media[Media] = MediaObjectType
    mdl = get_media_model()
    return registry.media[mdl]
