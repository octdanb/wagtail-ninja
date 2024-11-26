
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.managers import TaggableManager
from taggit.models import Tag

from wagtail_ninja.utils import resolve_queryset

from .structures import QuerySetList
from .base import BaseSchema
from ..converter import convert_django_field

@convert_django_field.register(TaggableManager)
@convert_django_field.register(ClusterTaggableManager)
def convert_tag_manager_to_string(field, registry=None):
    return TagObjectType()


class TagObjectType(BaseSchema):
    tag_id: int
    name: str

    # def resolve_tag_id(self, **kwargs):
    #     return self.id
    #
    # def resolve_name(self, **kwargs):
    #     return self.name


def TagsQuery():
    class Mixin:
        tag: TagObjectType
        tags: List[TagObjectType] = []

        def resolve_tag(self, info, id, **kwargs):
            try:
                return Tag.objects.get(pk=id)
            except Tag.DoesNotExist:
                return None

        def resolve_tags(self, info, **kwargs):
            return resolve_queryset(Tag.objects.all(), info, **kwargs)

    return Mixin
