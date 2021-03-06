from django.core.management.base import BaseCommand
from django_celery_beat.models import (
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule
)

class Command(BaseCommand):
    help = """
    will delette all periodic tasks, crontab and interval
    """

    def handle(self, *args, **options):
        """main controler."""
        PeriodicTask.objects.all().delete()
        IntervalSchedule.objects.all().delete()
        CrontabSchedule.objects.all().delete()
        self.stdout.write(f'PeriodicTask : {PeriodicTask.objects.all()}')
        self.stdout.write(f'IntervalSchedule : {IntervalSchedule.objects.all()}')
        self.stdout.write(f'CrontabSchedule : {CrontabSchedule.objects.all()}')
