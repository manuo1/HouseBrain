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

# app.conf.beat_schedule will create base celery tasks and setttings
# | you can change tasks settings from django admin at :
# | your_server/admin/django_celery_beat/periodictask/

app.conf.beat_schedule = {
    'Save temperatures every 5 minutes': {
        'task': 'sensors.tasks.read_and_save_temperatures',
        'schedule': crontab(minute='*/5'),
    },
    'Manage heating_periods & heaters 1 minute after saving temperatures': {
        'task': 'heating_manager.tasks.manage_heating_periods',
        'schedule': crontab(minute='1,6,11,16,21,26,31,36,41,46,51,56'),
    },
    'Check remaining power every 5 seconds': {
        'task': 'teleinformation.tasks.check_remaining_power',
        'schedule': 5,
    },

}
