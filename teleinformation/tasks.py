# Celery tasks

from celery import shared_task
from django.core import management

@shared_task
def read_and_save_teleinformation():
    """ run the manage.py command : teleinfo_history_save """
    # periodiode is configured in django admin
    management.call_command('teleinfo_history_save')

@shared_task
def check_remaining_power():
    """ run the manage.py command : power_monitoring """
    # periodiode is configured in django admin
    management.call_command('power_monitoring')
