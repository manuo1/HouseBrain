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


app.conf.beat_schedule = {
    # Get temperatures every 10 Minutes
    'Get temperatures every 10 minutes': {
        'task': 'sensors.tasks.get_temperatures',
        'schedule': crontab(minute='*/10'),
    },
}
    # crontab() mean Execute every minute
