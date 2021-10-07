# Celery tasks

from celery import shared_task
from django.core import management

@shared_task
def manage_heating_periods():
    """ run the manage.py command : manage_heating_periods """
    # periodiode is configured in django admin
    management.call_command('manage_heating_periods')
