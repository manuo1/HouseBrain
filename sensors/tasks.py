# Celery tasks

from celery import shared_task
from django.core import management

@shared_task
def read_and_save_temperatures():
    """ run the manage.py command : temperature_monitoring """
    # periodiode is configured in django admin
    management.call_command('temperature_monitoring')
