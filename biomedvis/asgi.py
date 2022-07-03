"""
ASGI config for visBioMedGitHub project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

CUR_DIR = os.path.basename(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', CUR_DIR + '.settings')

application = get_asgi_application()
