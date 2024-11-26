from __future__ import annotations
from datetime import datetime

from .base import BaseSchema
from wagtail.documents import get_document_model
from wagtail.documents.models import Document as WagtailDocument

from ..registry import registry
from ..utils import get_media_item_url, resolve_queryset
from .collections import CollectionObjectSchema
from .structures import QuerySetList
from .tags import TagObjectType


class DocumentObjectSchema(BaseSchema):
    """
    Base document type used if one isn't generated for the current model.
    All other node schemas extend this.
    """

    id: int
    title: str
    file: str
    created_at: datetime
    file_size: int
    file_hash: str
    url: str
    collection: CollectionObjectSchema = None
    tags: CollectionObjectSchema = None

    def resolve_url(self, info, **kwargs):
        """
        Get document file url.
        """
        return get_media_item_url(self)

    def resolve_tags(self, info, **kwargs):
        return self.tags.all()

    class Meta:
        model = WagtailDocument


def get_document_type():
    mdl = get_document_model()
    return registry.documents.get(mdl, DocumentObjectSchema)


def DocumentsQuery():
    mdl = get_document_model()
    mdl_type = get_document_type()

    class Mixin:
        document = graphene.Field(mdl_type, id=graphene.ID())
        documents = QuerySetList(
            graphene.NonNull(mdl_type),
            enable_search=True,
            required=True,
            collection=graphene.Argument(
                graphene.ID, description="Filter by collection id"
            ),
        )
        document_type: str

        def resolve_document(self, info, id, **kwargs):
            """Returns a document given the id, if in a public collection"""
            try:
                return mdl.objects.filter(
                    collection__view_restrictions__isnull=True
                ).get(pk=id)
            except mdl.DoesNotExist:
                return None

        def resolve_documents(self, info, **kwargs):
            """Returns all documents in a public collection"""
            qs = mdl.objects.filter(collection__view_restrictions__isnull=True)
            return resolve_queryset(qs, info, **kwargs)

        def resolve_document_type(self, info, **kwargs):
            return get_document_type()

    return Mixin
