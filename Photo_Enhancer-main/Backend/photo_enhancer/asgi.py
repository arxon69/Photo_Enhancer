"""
Django ASGI configuration for photo_enhancer project.

Exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from django.core.asgi import get_asgi_application
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_enhancer.settings')
django.setup()

application = get_asgi_application()