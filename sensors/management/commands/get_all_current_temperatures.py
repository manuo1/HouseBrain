from django.conf import settings
from django.utils import timezone

from sensors.models import TemperatureSensorManager

from django.core.management.base import BaseCommand

temperature_sensor_manager = TemperatureSensorManager()

class Command(BaseCommand):
    help = """
    will save in database all temperature sensors current temperatures
    """
    def add_arguments(self, get_all_current_temperatures):
        pass

    def handle(self, *args, **options):
        """main controler."""
        for sensor in temperature_sensor_manager.all_sensor():
            temperature_sensor_manager.save_temperature(
                self.read_temperature(sensor),
                sensor
            )

    def read_temperature(self, sensor):
        try:
            with open (sensor.sensor_folder_path + "/temperature") as file:
                temperature = file.readline()[:-1] #[:-1] to remove \n
            # reset the consecutive measurement error counter
            temperature_sensor_manager.reset_consecutive_errors(sensor)
        except FileNotFoundError:
            #if there is a reading error returns the default temperature
            temperature = 85000
            if not settings.DEBUG:
                self.stdout.write(
                    '{} - temperature reading error, cannot find path {}'
                    .format(
                        f'{timezone.now():%d/%m/%Y %H:%M}',
                        sensor.sensor_folder_path + "/temperature"
                        )
                    )
        # if the measurement returns an incorrect temperature,
        # | increments the sensosr error counter
        if temperature == 85000:
            temperature_sensor_manager.add_an_error(sensor)
        # add a false temperature measured in debug mode (no sensor connected)
        if settings.DEBUG:
            temperature = 54321
        return temperature
