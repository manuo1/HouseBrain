#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from dotenv import find_dotenv, load_dotenv

def main():
    """Run administrative tasks."""
    """ this part will load environment variable and designate the """
    """ right settings file to use depending on the environment"""
    load_dotenv(find_dotenv())
    environment = os.environ['ENVIRONMENT']
    os.environ.setdefault(
    	'DJANGO_SETTINGS_MODULE',
    	'housebrain_config.settings.{}'.format(environment),
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
