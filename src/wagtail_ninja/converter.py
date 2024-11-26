from functools import partial, singledispatch, wraps


@singledispatch
def convert_django_field(field, registry=None):
    raise Exception(
        f"Don't know how to convert the Django field {field} ({field.__class__})"
    )
