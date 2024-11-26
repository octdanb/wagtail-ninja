import logging
from typing import Dict
from ninja_extra import route, api_controller

logger = logging.getLogger(__name__)

from wagtail_ninja.schemas.pages import PageSchema
from wagtail_ninja.schemas.pages import get_specific_page

@api_controller('pages', tags=['Pages'], permissions=[])
class PagesController:

    @route.get('/', auth=None, by_alias=True, response={200: PageSchema}, operation_id="page-by")
    def page_by(self, url_path=None, slug=None, token=None, hostname=None):
        """
        Gets page by various queries

        """
        page = get_specific_page(
            slug=slug,
            url_path=url_path,
            token=token,
            hostname=hostname
        )

        return page

