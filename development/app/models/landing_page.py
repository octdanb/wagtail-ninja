from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.search import index
from app.mixins.headless_wagtail_preview import HeadlessWagtailPreview


class LandingPage(HeadlessWagtailPreview, Page):
    api_fields = ["extra_title", "body"]

    extra_title = RichTextField()
    body = RichTextField()


    # Search index configuration

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]


    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('extra_title'),
        FieldPanel('body'),
    ]

    promote_panels = [
    ]


    # Parent page / subpage type rules
    # parent_page_types = ['blog.BlogIndex']
    subpage_types = []
