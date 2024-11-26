import logging

from typing import Dict, List, Union
from ninja_extra import route, api_controller

logger = logging.getLogger(__name__)

# from wagtail_ninja.schemas.images import ImageObjectSchema
# from wagtail_ninja.schemas.pages import get_specific_page

@api_controller('images', tags=['Images'], permissions=[])
class ImagesController:

    @route.get('/', auth=None, by_alias=True, response={200: Dict}, operation_id="image-by")
    def image_by(self):
        """
        Gets image by various queries
        """
        return []

