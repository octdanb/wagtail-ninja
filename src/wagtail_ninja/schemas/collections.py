from typing import List
from wagtail.models import Collection
from .base import BaseSchema
from ..registry import registry
from ..utils import resolve_queryset
from .structures import QuerySetList


from typing import ForwardRef

class CollectionObjectSchema(BaseSchema):
    """
    Collection schema
    """

    class Meta:
        model = Collection

    id: int
    name : str
    # descendants: List[ForwardRef('CollectionObjectSchema')] = []
    # ancestors: List[ForwardRef('CollectionObjectSchema')] = []

    @staticmethod
    def resolve_descendants(instance):
        # only return public descendant Collections
        return instance.get_descendants().filter(view_restrictions__isnull=True)

    @staticmethod
    def resolve_ancestors(instance):
        # only return public descendant Collections
        return instance.get_ancestors().filter(view_restrictions__isnull=True)

CollectionObjectSchema.model_rebuild()


def CollectionsQuery():
    mdl = Collection
    mdl_type = registry.collections.get(mdl, CollectionObjectSchema)

    class Mixin:
        collections = QuerySetList(mdl_type, enable_search=False, required=True)

        # Return all collections
        def resolve_collections(self, info, **kwargs):
            # Only return public Collections
            qs = mdl.objects.filter(view_restrictions__isnull=True)
            return resolve_queryset(qs, info, **kwargs)

        def resolve_collection_type(self, info, **kwargs):
            return mdl_type

    return Mixin
