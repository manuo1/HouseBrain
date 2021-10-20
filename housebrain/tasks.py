# Celery tasks

from celery import shared_task
from django.core import management

@shared_task
def periodic_task_manager():
    """ run the manage.py command : periodic_task_manager """
    management.call_command('periodic_task_manager')
