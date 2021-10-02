"""
WSGI config for housebrain_config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from dotenv import find_dotenv, load_dotenv

""" this part will load environment variable and designate the """
""" right settings file to use depending on the environment"""
load_dotenv(find_dotenv())
environment = os.environ['ENVIRONMENT']
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'housebrain_config.settings.{}'.format(environment),
)

application = get_wsgi_application()
