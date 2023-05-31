"""
WSGI config for AnimeZ project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AnimeZ.settings')

application = get_wsgi_application()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
