"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_READ_DOT_ENV_FILE", "True")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "common.settings.production")

application = get_wsgi_application()
