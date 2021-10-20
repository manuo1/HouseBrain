from django.core import management
from django.core.management.base import BaseCommand
from django.utils import timezone

from sensors.models import TemperatureSensorManager
from teleinformation.models import TeleinfoManager

sensor_manager = TemperatureSensorManager()
teleinfo_manager = TeleinfoManager()

class Command(BaseCommand):
    help = """
    manager for periodic tasks except PowerMonitoring and
    read_and_save_temperatures
    """

    def handle(self, *args, **options):
        """main controler."""
        if self.run_task_at_minutes([1,6,11,16,21,26,31,36,41,46,51,56]):
            # applies setpoint temperatures to each room according
            #| to their heating period
            management.call_command('manage_heating_periods')
            #turns heaters on or off according to the setpoint temperatures
            management.call_command('manage_heaters')

        if self.run_task_at_minutes([0,30]):
            # save teleinfo
            #teleinfo_manager.save_teleinfo(self.teleinfo)
            # save tempertaures history
            sensor_manager.save_temperature_history()


    def run_task_at_minutes(self, minutes):
        return self.minute_now() in minutes

    def minute_now(self):
        return timezone.now().minute

    def second_now(self):
        return timezone.now().second

    def hour_now(self):
        return timezone.now().hour
