from ninja import NinjaAPI
from wagtail_ninja.router import WagtailNinjaPagesRouter, WagtailNinjaRedirectsRouter

ninja_api = NinjaAPI()
ninja_api.add_router("/pages/", WagtailNinjaPagesRouter())
ninja_api.add_router("/redirects/", WagtailNinjaRedirectsRouter())
