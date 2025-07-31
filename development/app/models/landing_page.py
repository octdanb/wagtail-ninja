from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
import wagtail.blocks as wagtail_blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.search import index
from app.mixins.headless_wagtail_preview import HeadlessWagtailPreview


class LandingPage(HeadlessWagtailPreview, Page):
    api_fields = ["extra_title", "content"]

    extra_title = RichTextField()
    body = RichTextField()


    content = StreamField(
        [
            ('char_block', wagtail_blocks.CharBlock()),
            ('richtext_block', wagtail_blocks.RichTextBlock()),
            ('text_block', wagtail_blocks.TextBlock()),
            ('email_block', wagtail_blocks.EmailBlock()),
            ('url_block', wagtail_blocks.URLBlock()),
        ],
        null=True,
        default=None,
        use_json_field=True,
    )


    # Search index configuration
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]


    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('extra_title'),
        FieldPanel('body'),
        FieldPanel('content'),
    ]

    promote_panels = [
    ]


    # Parent page / subpage type rules
    # parent_page_types = ['blog.BlogIndex']
    subpage_types = []
