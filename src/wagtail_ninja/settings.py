"""
Settings for Wagtail Ninja are all namespaced in the WAGTAIL_NINJA setting.
For example your project's `settings.py` file might look like this:
WAGTAIL_NINJA = {
    'APPS': ['home'],
    'ADD_SEARCH_HIT': True,
}
This module provides the `grapple_settings` object, that is used to access
Wagtail Ninja settings, checking for user settings first, then falling
back to the defaults.
"""

import logging

from django.conf import settings as django_settings
from django.test.signals import setting_changed


logger = logging.getLogger("wagtail_ninja")


DEFAULTS = {
    "APPS": [],
    "AUTO_CAMELCASE": True,
    "ALLOWED_IMAGE_FILTERS": None,
    "ADD_SEARCH_HIT": False,
    "PAGE_SIZE": 10,
    "MAX_PAGE_SIZE": 100,
    "RICHTEXT_FORMAT": "html",
    "PAGE_INTERFACE": "wagtail_ninja.schemas.interfaces.PageInterface",
    "SNIPPET_INTERFACE": "wagtail_ninja.schemas.interfaces.SnippetInterface",
}

# List of settings that have been deprecated
DEPRECATED_SETTINGS = [
    "WAGTAIL_NINJA_APPS",
    "WAGTAIL_NINJA_ADD_SEARCH_HIT",
    "WAGTAIL_NINJA_AUTO_CAMELCASE",
    "WAGTAIL_NINJA_ALLOWED_IMAGE_FILTERS",
]

# List of settings that have been removed
REMOVED_SETTINGS = []


class WagtailNinjaSettings:
    """
    A settings object that allows Wagtail Ninja settings to be accessed as
    properties. For example:
        from wagtail_ninja.settings import grapple_settings
        print(grapple_settings.APPS)
    Note:
    This is an internal class that is only compatible with settings namespaced
    under the WAGTAIL_NINJA name. It is not intended to be used by 3rd-party
    apps, and test helpers like `override_settings` may not work as expected.
    """

    def __init__(self, user_settings=None, defaults=None):
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.defaults = defaults or DEFAULTS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = self.__check_user_settings(
                getattr(django_settings, "WAGTAIL_NINJA", {})
            )
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f"Invalid WagtailNinja setting: '{attr}'")

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def __check_user_settings(self, user_settings):
        for setting in DEPRECATED_SETTINGS:
            if setting in user_settings or hasattr(django_settings, setting):
                new_setting = setting.replace("WAGTAIL_NINJA_", "")
                logger.warning(
                    f"The '{setting}' setting is deprecated and will be removed in the next release, use WAGTAIL_NINJA['{new_setting}'] instead."
                )
                if setting in user_settings:
                    user_settings[new_setting] = user_settings[setting]
                else:
                    user_settings[new_setting] = getattr(django_settings, setting)

        settings_doc_url = "https://wagtail-wagtail_ninja.readthedocs.io/en/latest/general-usage/settings.html"
        for setting in REMOVED_SETTINGS:
            if setting in user_settings:
                raise RuntimeError(
                    f"The '{setting}' setting has been removed. Please refer to '{settings_doc_url}' for available settings."
                )
        return user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


wagtail_ninja_settings = WagtailNinjaSettings(None, DEFAULTS)


def reload_wagtail_ninja_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "WAGTAIL_NINJA":
        wagtail_ninja_settings.reload()


setting_changed.connect(reload_wagtail_ninja_settings)
