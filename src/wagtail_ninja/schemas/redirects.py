import copy

from typing import List, Optional

from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Page, Site

from wagtail_ninja.schemas.sites import SiteObjectType

from .interfaces import get_page_interface
from .base import BaseSchema

class RedirectObjectSchema(BaseSchema):
    old_path: str
    old_url: str
    new_url: Optional[str]
    page: get_page_interface()
    site: SiteObjectType
    is_permanent: bool

    class Meta:
        name = "Redirect"

    def resolve_old_url(self, info, **kwargs) -> str:
        """
        Resolve the value of `old_url` using the `root_url` of the associated
        site and `old_path`.
        """

        return self.site.root_url + self.old_path

    def resolve_new_url(self, info, **kwargs) -> Optional[str]:
        """
        Resolve the value of `new_url`. If `redirect_page` is specified then its
        URL is prioritised.
        """

        return self.link

    # Return the page that's being redirected to, if at all.
    def resolve_page(self, info, **kwargs) -> Optional[Page]:
        if self.redirect_page is not None:
            return self.redirect_page.specific


class RedirectsQuery:
    redirects: List[RedirectObjectSchema]

    # Return all redirects.
    def resolve_redirects(self, info, **kwargs) -> List[Redirect]:
        """
        Resolve the query set of redirects. If `site` is None, a redirect works
        for all sites. To show this, a new redirect object is created for each
        of the sites.
        """

        redirects_qs = (
            Redirect.objects.select_related("redirect_page")
            .select_related("site")
            .all()
        )
        finalised_redirects: list[Redirect] = []  # Redirects to return in API.

        for redirect in redirects_qs:
            if redirect.site is None:
                # Duplicate Redirect for each Site as it applies to all Sites.
                for site in Site.objects.all():
                    _new_redirect = copy.deepcopy(redirect)
                    _new_redirect.site = site
                    finalised_redirects.append(_new_redirect)
            else:
                finalised_redirects.append(redirect)
        return finalised_redirects
