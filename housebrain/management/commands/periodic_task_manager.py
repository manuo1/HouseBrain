from django.core.management.base import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
    help = """
    manager for periodic tasks except PowerMonitoring
    """

    def handle(self, *args, **options):
        """main controler."""
        if self.run_task_at_minutes([0,5,10,15,20,25,30,35,40,45,50,55]):
            # read and save in db the curent temperatures
            management.call_command('read_and_save_temperatures')

        if self.run_task_at_minutes([1,6,11,16,21,26,31,36,41,46,51,56]):
            # applies setpoint temperatures to each room according
            #| to their heating period
            management.call_command('manage_heating_periods')
            #turns heaters on or off according to the setpoint temperatures
            management.call_command('manage_heaters')

    def run_task_at_minutes(self, minutes):
        return self.minute_now() in minutes

    def minute_now(self):
        return timezone.now().minute

    def second_now(self):
        return timezone.now().second

    def hour_now(self):
        return timezone.now().hour
