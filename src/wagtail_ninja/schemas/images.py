from __future__ import annotations

from datetime import datetime

from typing import TYPE_CHECKING, List
from ninja import Field
from wagtail.images import get_image_model
from wagtail.images.models import Image as WagtailImage
from wagtail.images.models import Rendition as WagtailImageRendition
from wagtail.images.utils import to_svg_safe_spec

from wagtail_ninja.registry import registry
from wagtail_ninja.settings import wagtail_ninja_settings
from wagtail_ninja.utils import get_media_item_url, resolve_queryset

from .base import BaseSchema
from .collections import CollectionObjectSchema
from .structures import QuerySetList
from .tags import TagObjectType




def get_image_type():
    return registry.images.get(get_image_model(), ImageObjectSchema)


def get_rendition_type():
    rendition_mdl = get_image_model().renditions.rel.related_model
    return registry.images.get(rendition_mdl, ImageRenditionObjectSchema)


class ImageRenditionSchema:
    max: str = None
    min: str = None
    width: int = None
    height: int = None
    fill: str = None
    format: str = None
    bgcolor: str = None
    jpegquality: int = None
    webpquality: int = None
    preserve_svg: bool = None



def get_src_set_field_kwargs() -> dict:
    """
    Returns a list of kwargs for the srcSet field.
    Extracted for convenience, to accommodate for the conditional logic needed for various Wagtail versions.
    """
    kwargs = {
        "sizes": List[int],
        "format": str,
        "preserve_svg": bool,
    }

    return kwargs


def rendition_allowed(filter_specs: str) -> bool:
    """Checks a given rendition filter is allowed"""
    allowed_filters = wagtail_ninja_settings.ALLOWED_IMAGE_FILTERS
    if allowed_filters is None or not isinstance(allowed_filters, (list, tuple)):
        return True

    return filter_specs in allowed_filters


class ImageRenditionObjectSchema(BaseSchema):
    id: int
    file: str
    image: lambda: get_image_type()
    filter_spec: str
    width: int
    height: int
    focal_point_key: str
    focal_point: str = None
    url: str
    alt: str
    background_position_style: str

    class Meta:
        model = WagtailImageRendition

    def resolve_url(instance: WagtailImageRendition, info, **kwargs):
        return instance.full_url


class ImageObjectSchema(BaseSchema):
    id: int
    title: str
    file: str
    width: int
    height: int
    created_at: datetime
    focal_point_x: int = None
    focal_point_y: int = None
    focal_point_width: int = None
    focal_point_height: int = None
    file_size: int = None
    file_hash: str
    src: str
    url: str
    aspect_ratio: float
    sizes: str
    # collection: CollectionObjectSchema = None
    tags: List[TagObjectType] = []
    rendition: ImageRenditionSchema = None
    src_set: get_src_set_field_kwargs()
    is_svg: bool

    class Meta:
        model = WagtailImage

    @staticmethod
    def resolve_rendition(instance: WagtailImage, **kwargs) -> WagtailImageRendition | None:
        """
        Render a custom rendition of the current image.
        """
        preserve_svg = kwargs.pop("preserve_svg", True)
        filter_specs = "|".join([f"{key}-{val}" for key, val in kwargs.items()])

        # Only allow the defined filters (thus renditions)
        if not rendition_allowed(filter_specs):
            raise TypeError(
                "Invalid filter specs. Check the `ALLOWED_IMAGE_FILTERS` setting."
            )

        if instance.is_svg() and preserve_svg:
            # when dealing with SVGs, we want to limit the filter specs to those that are safe
            filter_specs = to_svg_safe_spec(filter_specs)
            if not filter_specs:
                # if there are no valid filters, fall back to the original
                filter_specs = "original"

            if not filter_specs:
                raise TypeError(
                    "No valid filter specs for SVG. "
                    "See https://docs.wagtail.org/en/stable/topics/images.html#svg-images for details."
                )

        # previously we wrapped this in a try/except SourceImageIOError block.
        # Removed to allow the error to bubble up in the response ("errors") and be handled by the user.
        return instance.get_rendition(filter_specs)

    @staticmethod
    def resolve_url(instance: WagtailImage, **kwargs) -> str:
        """
        Get the uploaded image url.
        """
        return get_media_item_url(instance)

    @staticmethod
    def resolve_src(instance: WagtailImage, **kwargs) -> str:
        """
        Deprecated. Use the `url` attribute.
        """
        return get_media_item_url(instance)

    @staticmethod
    def resolve_aspect_ratio( instance: WagtailImage, **kwargs):
        """
        Calculate aspect ratio for the image.
        """
        return instance.width / instance.height

    @staticmethod
    def resolve_sizes(instance: WagtailImage, **kwargs) -> str:
        return f"(max-width: {instance.width}px) 100vw, {instance.width}px"

    @staticmethod
    def resolve_tags(instance: WagtailImage, **kwargs):
        return instance.tags.all()

    @staticmethod
    def resolve_src_set(
        instance: WagtailImage,
        sizes: list[int],
        format: str | None = None,
        *,
        preserve_svg: bool = True,
        **kwargs,
    ) -> str:
        """
        Generate app set of renditions.
        """
        filter_suffix = f"|format-{format}" if format else ""
        format_kwarg = {"format": format} if format else {}
        if instance.file.name is not None:
            rendition_list = [
                ImageObjectSchema.resolve_rendition(
                    instance,
                    info,
                    width=width,
                    preserve_svg=preserve_svg,
                    **format_kwarg,
                )
                for width in sizes
                if rendition_allowed(f"width-{width}{filter_suffix}")
            ]

            return ", ".join(
                [
                    f"{get_media_item_url(img)} {img.width}w"
                    for img in rendition_list
                    if img is not None
                ]
            )

        return ""

    @staticmethod
    def resolve_is_svg(instance: WagtailImage, **kwargs) -> bool:
        return instance.is_svg()


def ImagesQuery():
    mdl = get_image_model()
    mdl_type = get_image_type()

    class Mixin:
        image: int = None
        images: List[int] = []
        image_type: str = None

        def resolve_image(parent, info, id, **kwargs):
            """Returns an image given the id, if in a public collection"""
            try:
                return (
                    mdl.objects.filter(collection__view_restrictions__isnull=True)
                    .prefetch_renditions()
                    .get(pk=id)
                )
            except mdl.DoesNotExist:
                return None

        def resolve_images(parent, info, **kwargs):
            """Returns all images in a public collection"""
            return resolve_queryset(
                mdl.objects.filter(
                    collection__view_restrictions__isnull=True
                ).prefetch_renditions(),
                info,
                **kwargs,
            )

        # Give name of the image type, used to generate mixins
        def resolve_image_type(parent, info, **kwargs):
            return mdl_type

    return Mixin
