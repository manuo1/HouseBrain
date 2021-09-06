# Celery tasks

from celery import shared_task
from django.core import management

@shared_task
def read_and_save_temperatures():
    """ run the manage.py command : temperatures_save """
    # periodiode is configured in django admin
    management.call_command('temperatures_save')

@shared_task
def save_temperature_history():
    """ run the manage.py command : save_temperature_history """
    # periodiode is configured in django admin
    management.call_command('save_temperature_history')
