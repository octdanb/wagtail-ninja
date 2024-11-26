from typing import List
from ..registry import registry
from .interfaces import get_snippet_interface


def SnippetsQuery():
    class Mixin:
        snippets = List[get_snippet_interface()]

        def resolve_snippets(self, info, **kwargs):
            snippet_objects = []
            for snippet in registry.snippets:
                for object in snippet._meta.model.objects.all():
                    snippet_objects.append(object)

            return snippet_objects

    return Mixin