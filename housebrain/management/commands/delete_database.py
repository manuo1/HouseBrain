from django.core.management.base import BaseCommand
from django_celery_beat.models import (
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule
)

from heaters.models import Heater
from heating_manager.models import (
    HeatingMode,
    HeatingPeriod,
    CurrentHeatingMode
)
from rooms.models import Room
from sensors.models import (TemperatureSensor, TemperatureHistory)
from teleinformation.models import (PowerMonitoring, TeleinformationHistory)


class Command(BaseCommand):
    help = """
    will delette all data in database
    """
    def add_arguments(self, delete_database):
        pass

    def handle(self, *args, **options):
        """main controler."""
        PeriodicTask.objects.all().delete()
        IntervalSchedule.objects.all().delete()
        CrontabSchedule.objects.all().delete()
        Heater.objects.all().delete()
        HeatingMode.objects.all().delete()
        HeatingPeriod.objects.all().delete()
        CurrentHeatingMode.objects.all().delete()
        Room.objects.all().delete()
        TemperatureSensor.objects.all().delete()
        TemperatureHistory.objects.all().delete()
        PowerMonitoring.objects.all().delete()
        TeleinformationHistory.objects.all().delete()
