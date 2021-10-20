from django.conf import settings
from django.utils import timezone
from housebrain_config.settings.constants import (
    DEBUG_TEMPERATURE,
    ERROR_TEMPERATURE,
    TEMPERATURE_FILE,
)
from sensors.models import TemperatureSensorManager
from django.core.management.base import BaseCommand

sensor_manager = TemperatureSensorManager()

class Command(BaseCommand):
    help = """
    will save in database all temperature sensors current temperatures
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--readonly',
            action='store_true',
            help='display temperatures in the console without saving'
        )

    def handle(self, *args, **options):
        """main controler."""
        if settings.UNPLUGGED_MODE:
            self.stdout.write("---- UNPLUGGED_MODE ----")
        for sensor in sensor_manager.all_sensors():
            temperature = self.read_temperature(sensor)
            if options['readonly']:
                self.stdout.write(
                    f'{sensor.sensor_folder_path} : {temperature}'
                )
            else:
                sensor_manager.save_temperature(temperature, sensor)

    def read_temperature(self, sensor):
        if settings.UNPLUGGED_MODE:
            temperature = DEBUG_TEMPERATURE
        else :
            temperature = self.read_sensor_file(sensor)
            if temperature:
                temperature = self.str_to_int(temperature)

            if temperature and not temperature == 0:
                sensor_manager.reset_consecutive_errors(sensor)
            else:
                temperature = ERROR_TEMPERATURE
                sensor_manager.add_an_error(sensor)
        return temperature

    def str_to_int(self,str_temperature):
        try:
            return int(str_temperature)
        except ValueError:
             return None

    def read_sensor_file(self,sensor):
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
        return temperature
