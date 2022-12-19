"""
WSGI config for visBioMedGitHub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

CUR_DIR_NAME = os.path.basename(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biomedvis.settings')

application = get_wsgi_application()
