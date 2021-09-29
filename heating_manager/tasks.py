# Celery tasks

from celery import shared_task
from django.core import management

@shared_task
def manage_heaters():
    """ run the manage.py command : manage_heaters """
    # periodiode is configured in django admin
    management.call_command('manage_heaters')
