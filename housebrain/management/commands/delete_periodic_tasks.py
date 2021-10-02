from sensors.models import TemperatureSensorManager
from django.core.management.base import BaseCommand
from django_celery_beat.models import (
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule
)

temperature_sensor_manager = TemperatureSensorManager()

class Command(BaseCommand):
    help = """
    will delette all periodic tasks, crontab and interval
    """
    def add_arguments(self, delete_periodic_tasks):
        pass

    def handle(self, *args, **options):
        """main controler."""
        PeriodicTask.objects.all().delete()
        IntervalSchedule.objects.all().delete()
        CrontabSchedule.objects.all().delete()
