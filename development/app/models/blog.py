from django.db import models

from modelcluster.fields import ParentalKey
from ninja import Schema

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.search import index
from app.mixins.headless_wagtail_preview import HeadlessMixin


class BlogPage(HeadlessMixin, Page):
    api_fields = ["body", "date", "feed_image", "related_links"] #  "related_links" not working yet

    body = RichTextField()
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    # Search index configuration
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.FilterField('date'),
    ]


    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('body'),
        FieldPanel('feed_image'),
        InlinePanel('related_links', heading="Related links", label="Related link"),
    ]

    def resolve_related_links(self): # TOOD: work out how to do draft related links
       related = BlogPageRelatedLink.objects.filter(page__id=self.id)

       class RelatedLinksSchema(Schema):
           page_id: int
           name: str
           url: str

           @staticmethod
           def resolve_page_id(related_link):
               return related_link.page.id


       return [ RelatedLinksSchema.from_orm(x) for x in related ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        FieldPanel('feed_image'),
    ]  + Page.promote_panels

    # Parent page / subpage type rules
    subpage_types = []


class BlogPageRelatedLink(Orderable):
    api_fields = ["page", "name", "url"]

    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='related_links')
    name = models.CharField(max_length=255)
    url = models.URLField()

    panels = [
        FieldPanel('name'),
        FieldPanel('url'),
    ]

