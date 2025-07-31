from django.utils.http import urlencode
from wagtail_headless_preview.models import HeadlessMixin, HeadlessPreviewMixin


class HeadlessWagtailPreview(HeadlessPreviewMixin):
    def get_preview_url(self, token, x):
        print(x)

        if self.has_unpublished_changes:
            return (
                    self.url
                    + "?"
                    + urlencode(
                {
                    "content_type": self.localized_draft.get_content_type_str(),
                    "token": token,
                    "slug": self.slug,
                    "draft": 'true',
                    "in_preview_panel": 'true'
                }
            )
            )
        return (
                self.url
                + "?"
                + urlencode(
            {
                "content_type": self.get_content_type_str(),
                "token": token,
                "url": self.slug,
                "in_preview_panel": 'true'}
        )
        )
