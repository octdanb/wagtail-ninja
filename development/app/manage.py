#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings.development')
    from django.core.management import execute_from_command_line

    if os.environ['DJANGO_SETTINGS_MODULE'] == 'app.settings.development':
        from app.settings.development import WAGTAILADMIN_BASE_URL

        print(f"Starting django on {WAGTAILADMIN_BASE_URL}")

    execute_from_command_line(sys.argv)