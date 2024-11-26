from ninja_extra import NinjaExtraAPI, exceptions
from .api.controllers.pages import PagesController
from .api.controllers.images import ImagesController

api = NinjaExtraAPI()
api.register_controllers(PagesController)
api.register_controllers(ImagesController)


from pprint import pprint as pp

def api_exception_handler(request, exc):
    headers = {}

    if isinstance(exc.detail, (list, dict)):
        data = exc.detail
    else:
        data = {"detail": exc.detail}

    response = api.create_response(request, data, status=exc.status_code)
    for k, v in headers.items():
        response.setdefault(k, v)

    pp(response.__dict__)
    return response

def api_validation_handler(request, exc):
    headers = {}

    if isinstance(exc.detail, (list, dict)):
        data = exc.detail
    else:
        data = {"detail": exc.detail}

    response = api.create_response(request, data, status=exc.status_code)
    for k, v in headers.items():
        response.setdefault(k, v)

    pp(response.__dict__)
    return response


api.exception_handler(exceptions.ValidationError)(api_validation_handler)
