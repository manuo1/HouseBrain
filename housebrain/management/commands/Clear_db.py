from django.core.management.base import BaseCommand
from heaters.models import Heater
from rooms.models import Room
from sensors.models import TemperatureSensor
from teleinformation.models import (
    PowerMonitoring,
    TeleinformationHistory
)
from django_celery_beat.models import (
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule
)

class Command(BaseCommand):
    help = """
    will delette all data in tables
    """

    def handle(self, *args, **options):
        """main controler."""
        self.stdout.write(f'PeriodicTask : {PeriodicTask.objects.all().count()}')
        PeriodicTask.objects.all().delete()
        self.stdout.write(f'--> PeriodicTask : {PeriodicTask.objects.all().count()}')

        self.stdout.write(f'IntervalSchedule : {IntervalSchedule.objects.all().count()}')
        IntervalSchedule.objects.all().delete()
        self.stdout.write(f'--> IntervalSchedule : {IntervalSchedule.objects.all().count()}')

        self.stdout.write(f'CrontabSchedule : {CrontabSchedule.objects.all().count()}')
        CrontabSchedule.objects.all().delete()
        self.stdout.write(f'--> CrontabSchedule : {CrontabSchedule.objects.all().count()}')

        self.stdout.write(f'Heater : {Heater.objects.all().count()}')
        Heater.objects.all().delete()
        self.stdout.write(f'--> Heater : {Heater.objects.all().count()}')

        self.stdout.write(f'Room : {Room.objects.all().count()}')
        Room.objects.all().delete()
        self.stdout.write(f'--> Room : {Room.objects.all().count()}')

        self.stdout.write(f'TemperatureSensor : {TemperatureSensor.objects.all().count()}')
        TemperatureSensor.objects.all().delete()
        self.stdout.write(f'--> TemperatureSensor : {TemperatureSensor.objects.all().count()}')

        self.stdout.write(f'PowerMonitoring : {PowerMonitoring.objects.all().count()}')
        PowerMonitoring.objects.all().delete()
        self.stdout.write(f'--> PowerMonitoring : {PowerMonitoring.objects.all().count()}')

        self.stdout.write(f'TeleinformationHistory : {TeleinformationHistory.objects.all().count()}')
        TeleinformationHistory.objects.all().delete()
        self.stdout.write(f'--> TeleinformationHistory : {TeleinformationHistory.objects.all().count()}')
