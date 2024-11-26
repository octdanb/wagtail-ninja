from django.apps import AppConfig


class WagtailNinja(AppConfig):
    name = "wagtail_ninja"

    def ready(self):
        """
        Import all the django apps defined in django settings then process each model
        in these apps and create pydantic schemas from them.
        """

        # from .actions import import_apps
        # from .actions import load_type_fields
        # from .schemas.streamfield import register_streamfield_blocks
        #
        # import_apps()
        # load_type_fields()
        # register_streamfield_blocks()
        # print("done")

