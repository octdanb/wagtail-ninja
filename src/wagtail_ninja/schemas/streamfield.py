from typing import Optional, List

import wagtail
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks
import wagtail.snippets.blocks

from wagtail import blocks
from wagtail.embeds.blocks import EmbedValue
from wagtail.embeds.embeds import get_embed
from wagtail.embeds.exceptions import EmbedException
from wagtail.fields import StreamField

from ..registry import registry
from ..types.json import JSON
from ..converter import convert_django_field
from .interfaces import StreamFieldInterface
from .rich_text import RichText as RichTextType
from .base import BaseSchema

class GenericStreamFieldInterface(BaseSchema):
    @staticmethod
    def serialize(stream_value):
        try:
            return stream_value.raw_data
        except AttributeError:
            return stream_value.stream_data

@convert_django_field.register(StreamField)
def convert_stream_field(field, registry=None):
    return GenericStreamFieldInterface(
        description=field.help_text, required=not field.null
    )


def generate_streamfield_union(types):
    class StreamfieldUnion(Union):
        class Meta:
            types = types

        @classmethod
        def resolve_type(cls, instance, info):
            """
            If block has a custom Graphene Node type in registry then use it,
            otherwise use generic block type.
            """
            mdl = type(instance.block)
            if mdl in registry.streamfield_blocks:
                return registry.streamfield_blocks[mdl]

            return registry.streamfield_blocks["generic-block"]

    return StreamfieldUnion


class StructBlockItem:
    id = None
    block = None
    value = None

    def __init__(self, id, block, value=""):
        self.id = id
        self.block = block
        self.value = value


class StructBlock(BaseSchema):
    # class Meta:
    #     interfaces = (StreamFieldInterface,)

    blocks: List[StreamFieldInterface]

    def resolve_blocks(self, info, **kwargs):
        stream_blocks = []

        if issubclass(type(self.value), blocks.stream_block.StreamValue):
            # self: StreamChild, block: StreamBlock, value: StreamValue
            stream_data = self.value[0]
            child_blocks = self.value.stream_block.child_blocks
        else:
            # This occurs when StreamBlock is child of StructBlock
            # self: StructBlockItem, block: StreamBlock, value: list
            stream_data = self.value
            child_blocks = self.block.child_blocks

        for field, value in stream_data.items():
            block = dict(child_blocks)[field]
            if isinstance(value, int) and (
                issubclass(type(block), blocks.ChooserBlock)
                or not issubclass(type(block), blocks.StructBlock)
            ):
                value = block.to_python(value)

            stream_blocks.append(StructBlockItem(field, block, value))

        return stream_blocks


class StreamBlock(StructBlock):
    class Meta:
        interfaces = (StreamFieldInterface,)

    def resolve_blocks(self, info, **kwargs):
        child_blocks = self.value.stream_block.child_blocks

        return [
            StructBlockItem(
                id=stream.id, block=child_blocks[stream.block_type], value=stream.value
            )
            for stream in self.value
        ]


class StreamFieldBlock(BaseSchema):
    value: str

    class Meta:
        interfaces = (StreamFieldInterface,)


class CharBlock(BaseSchema):
    value: str

    class Meta:
        interfaces = (StreamFieldInterface,)


class TextBlock(BaseSchema):
    value: str

    class Meta:
        interfaces = (StreamFieldInterface,)


class EmailBlock(BaseSchema):
    value: str

    class Meta:
        interfaces = (StreamFieldInterface,)


class IntegerBlock(BaseSchema):
    value: int

    class Meta:
        interfaces = (StreamFieldInterface,)


class FloatBlock(BaseSchema):
    value: float

    class Meta:
        interfaces = (StreamFieldInterface,)


class DecimalBlock(BaseSchema):
    value: float

    class Meta:
        interfaces = (StreamFieldInterface,)


class RegexBlock(BaseSchema):
    value: str

    class Meta:
        interfaces = (StreamFieldInterface,)


class URLBlock(BaseSchema):
    value: str

    class Meta:
        interfaces = (StreamFieldInterface,)


class BooleanBlock(BaseSchema):
    value: bool

    class Meta:
        interfaces = (StreamFieldInterface,)


class DateBlock(BaseSchema):
    value: str

    class Meta:
        interfaces = (StreamFieldInterface,)

    def resolve_value(self, info, **kwargs):
        format = kwargs.get("format")
        if format:
            return self.value.strftime(format)
        return self.value


class DateTimeBlock(DateBlock):
    class Meta:
        interfaces = (StreamFieldInterface,)


class TimeBlock(DateBlock):
    class Meta:
        interfaces = (StreamFieldInterface,)


class RichTextBlock(BaseSchema):
    value: str

    class Meta:
        interfaces = (StreamFieldInterface,)

    def resolve_value(self, info, **kwargs):
        return RichTextType.serialize(self.value.source)


class RawHTMLBlock(BaseSchema):
    value: str

    class Meta:
        interfaces = (StreamFieldInterface,)


class BlockQuoteBlock(BaseSchema):
    value: str

    class Meta:
        interfaces = (StreamFieldInterface,)


class ChoiceOption(BaseSchema):
    key: str
    value: str


class ChoiceBlock(BaseSchema):
    value: str
    choices: List[ChoiceOption]

    class Meta:
        interfaces = (StreamFieldInterface,)

    def resolve_choices(self, info, **kwargs):
        choices = []
        for key, value in self.block._constructor_kwargs["choices"]:
            choice = ChoiceOption(key, value)
            choices.append(choice)
        return choices


def get_embed_url(instance):
    return instance.value.url if hasattr(instance, "value") else instance.url


def get_embed_object(instance):
    try:
        return get_embed(get_embed_url(instance))
    except EmbedException:
        pass


class EmbedBlock(BaseSchema):
    value: str
    url: str
    embed: Optional[str]
    raw_embed: Optional[JSON]

    class Meta:
        interfaces = (StreamFieldInterface,)

    def resolve_url(self: EmbedValue, info, **kwargs) -> str:
        return get_embed_url(self)

    def resolve_raw_value(self: EmbedValue, info, **kwargs) -> str:
        if isinstance(self, EmbedValue):
            return self
        return StreamFieldInterface.resolve_raw_value(info, **kwargs)

    def resolve_value(self: EmbedValue, info, **kwargs) -> str:
        return EmbedBlock.resolve_raw_value(self, info, **kwargs)

    def resolve_embed(self: EmbedValue, info, **kwargs) -> Optional[str]:
        embed = get_embed_object(self)
        if embed:
            return embed.html

    def resolve_raw_embed(self: EmbedValue, info, **kwargs) -> Optional[str]:
        embed = get_embed_object(self)
        if embed:
            return {
                "title": embed.title,
                "type": embed.type,
                "thumbnail_url": embed.thumbnail_url,
                "width": embed.width,
                "height": embed.height,
                "html": embed.html,
            }


class StaticBlock(BaseSchema):
    value: str

    class Meta:
        interfaces = (StreamFieldInterface,)


class ListBlock(BaseSchema):
    items: List[StreamFieldInterface]

    class Meta:
        interfaces = (StreamFieldInterface,)

    def resolve_items(self, info, **kwargs):
        # Get the nested StreamBlock type
        block_type = self.block.child_block
        # Return a list of GraphQL schemas from the list of values
        return [StructBlockItem(self.id, block_type, item) for item in self.value]


registry.streamfield_blocks.update(
    {
        "generic-block": StreamFieldBlock,
        blocks.CharBlock: CharBlock,
        blocks.TextBlock: TextBlock,
        blocks.EmailBlock: EmailBlock,
        blocks.IntegerBlock: IntegerBlock,
        blocks.FloatBlock: FloatBlock,
        blocks.DecimalBlock: DecimalBlock,
        blocks.RegexBlock: RegexBlock,
        blocks.URLBlock: URLBlock,
        blocks.BooleanBlock: BooleanBlock,
        blocks.DateBlock: DateBlock,
        blocks.TimeBlock: TimeBlock,
        blocks.DateTimeBlock: DateTimeBlock,
        blocks.RichTextBlock: RichTextBlock,
        blocks.RawHTMLBlock: RawHTMLBlock,
        blocks.BlockQuoteBlock: BlockQuoteBlock,
        blocks.ChoiceBlock: ChoiceBlock,
        blocks.StreamBlock: StreamBlock,
        blocks.StructBlock: StructBlock,
        blocks.StaticBlock: StaticBlock,
        blocks.ListBlock: ListBlock,
        wagtail.embeds.blocks.EmbedBlock: EmbedBlock,
    }
)


def register_streamfield_blocks():
    from .documents import get_document_type
    from .images import get_image_type
    from .interfaces import get_page_interface, get_snippet_interface

    class PageChooserBlock(BaseSchema):
        page: get_page_interface()

        class Meta:
            interfaces = (StreamFieldInterface,)

        def resolve_page(self, info, **kwargs):
            return self.value.specific

    class DocumentChooserBlock(BaseSchema):
        document: get_document_type()

        class Meta:
            interfaces = (StreamFieldInterface,)

        def resolve_document(self, info, **kwargs):
            return self.value

    class ImageChooserBlock(BaseSchema):
        image: get_image_type()

        class Meta:
            interfaces = (StreamFieldInterface,)

        def resolve_image(self, info, **kwargs):
            return self.value

    registry.streamfield_blocks.update(
        {
            blocks.PageChooserBlock: PageChooserBlock,
            wagtail.documents.blocks.DocumentChooserBlock: DocumentChooserBlock,
            wagtail.images.blocks.ImageChooserBlock: ImageChooserBlock,
        }
    )

    class SnippetChooserBlock(BaseSchema):
        snippet: get_snippet_interface()

        class Meta:
            interfaces = (StreamFieldInterface,)

        def resolve_snippet(self, info, **kwargs):
            return self.value

    registry.streamfield_blocks.update(
        {
            wagtail.snippets.blocks.SnippetChooserBlock: SnippetChooserBlock,
        }
    )
