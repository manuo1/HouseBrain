# Celery tasks

from celery import shared_task
from django.core import management

@shared_task
def get_temperatures():
    """ run the manage.py command : temperatures_now """
    # periodiode is configured in django admin
    management.call_command('temperatures_now')
