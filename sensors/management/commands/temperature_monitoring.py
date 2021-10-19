from django.conf import settings
from django.utils import timezone
from housebrain_config.settings.constants import (
    DEBUG_TEMPERATURE,
    ERROR_TEMPERATURE,
    TEMPERATURE_FILE,
    TEMPERATURE_HISTORY_DELTA,
)
from sensors.models import TemperatureSensorManager
from django.core.management.base import BaseCommand

sensor_manager = TemperatureSensorManager()

class Command(BaseCommand):
    help = """
    will save in database all temperature sensors current temperatures
    """
    def add_arguments(self, temperature_monitoring):
        pass

    def handle(self, *args, **options):
        """main controler."""
        for sensor in sensor_manager.all_sensors():
            sensor_manager.save_temperature(
                self.read_temperature(sensor),
                sensor
                )

        if self.it_s_time_to_save_temperature_history():
            sensor_manager.save_temperature_history()

    def it_s_time_to_save_temperature_history(self):
        return timezone.now().minute % TEMPERATURE_HISTORY_DELTA == 0

    def read_temperature(self, sensor):
        if settings.UNPLUGGED_MODE:
            temperature = DEBUG_TEMPERATURE
            self.stdout.write("reading temp in ---- UNPLUGGED_MODE ----")
        else :
            temperature = None
            try:
                with open (
                    sensor.sensor_folder_path + TEMPERATURE_FILE
                ) as file:
                    temperature = file.readline()
            except FileNotFoundError:
                pass
            except Exception as e:
                self.stdout.write(f'error during reading temperature :\n{e}')

            if temperature:
                try:
                    temperature = int(temperature)
                except ValueError:
                     temperature = None

            if temperature and not temperature == 0:
                sensor_manager.reset_consecutive_errors(sensor)
            else:
                temperature = ERROR_TEMPERATURE
                sensor_manager.add_an_error(sensor)

        return temperature
