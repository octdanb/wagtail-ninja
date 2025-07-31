WEB_SITE_ROOT_URL = "http://localhost:3000/preview/"

WAGTAIL_HEADLESS_PREVIEW = {
    "SERVE_BASE_URL": WEB_SITE_ROOT_URL,
    "REDIRECT_ON_PREVIEW": False, # Must be false for multisite preview to work.
    "ENFORCE_TRAILING_SLASH": True,
    "CLIENT_URLS": {
        "default": WEB_SITE_ROOT_URL,
    }
}
