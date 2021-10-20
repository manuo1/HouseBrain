# Celery tasks

from celery import shared_task
from django.core import management

@shared_task
def check_remaining_power():
    """ run the manage.py command : power_monitoring """
    management.call_command('power_monitoring')
