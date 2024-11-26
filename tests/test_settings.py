from django.test import TestCase, override_settings

from wagtail_ninja.settings import (
    DEPRECATED_SETTINGS,
    REMOVED_SETTINGS,
    GrappleSettings,
    wagtail_ninja_settings,
)


class TestSettings(TestCase):
    def test_warning_raised_on_deprecated_setting(self):
        """
        Make sure user is alerted with an warning when a deprecated setting is set.
        """
        if len(DEPRECATED_SETTINGS) > 0:
            with self.assertLogs("wagtail_ninjawagtail_ninja", level="WARNING"):
                GrappleSettings({DEPRECATED_SETTINGS[0]: True})

    def test_error_raised_on_removed_setting(self):
        """
        Make sure user is alerted with an error when a removed setting is set.
        """
        if len(REMOVED_SETTINGS) > 0:
            with self.assertRaises(RuntimeError):
                GrappleSettings({REMOVED_SETTINGS[0]: True})

    def test_compatibility_with_override_settings(self):
        """
        Usage of grapple_settings is bound at import time:
            from wagtail_ninja.settings import grapple_settings
        setting_changed signal hook must ensure bound instance is refreshed.
        """
        self.assertEqual(wagtail_ninja_settings.PAGE_SIZE, 10)

        with override_settings(WAGTAIL_NINJA={"PAGE_SIZE": 5}):
            self.assertEqual(wagtail_ninja_settings.PAGE_SIZE, 5)

        self.assertEqual(wagtail_ninja_settings.PAGE_SIZE, 10)
