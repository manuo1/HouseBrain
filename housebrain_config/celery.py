import os

from celery import Celery
from celery.schedules import crontab
from dotenv import find_dotenv, load_dotenv

# Set the default Django settings module for the 'celery' program.
""" this part will load environment variable and designate the """
""" right settings file to use depending on the environment"""
load_dotenv(find_dotenv())
environment = os.environ['ENVIRONMENT']
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'housebrain_config.settings.{}'.format(environment),
)

app = Celery('housebrain_config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# app.conf.beat_schedule create celery tasks and setttings

app.conf.beat_schedule = {
    'periodic tasks manager': {
        'task': 'housebrain.tasks.periodic_task_manager',
        'schedule': crontab(minute='*'),
    },
    'Check remaining power every 5 seconds': {
        'task': 'teleinformation.tasks.check_remaining_power',
        'schedule': 5,
    },
}
