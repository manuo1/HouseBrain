from django.conf import settings
from django.utils import timezone
from housebrain_config.settings.constants import (
    DEBUG_TEMPERATURE,
    ERROR_TEMPERATURE,
    TEMPERATURE_FILE,
    SENSOR_READING_MAX_ATTEMPTS as max_attemps,
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
            temperature = None
            attempt = 0
            while not temperature and attempt != max_attemps:
                temperature = self.read_temperature(sensor)
                attempt += 1
            if temperature:
                sensor.consecutive_errors = 0
                sensor.is_malfunctioning = False

            else:
                temperature = ERROR_TEMPERATURE
                sensor.consecutive_errors +=1
                sensor.cumulative_errors +=1
                sensor.is_malfunctioning = True

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
            temperature = self.str_to_int(self.read_sensor_file(sensor))
            # no diff between 0 reading value or error reading value
            #| so don't save 0 value
            if temperature == 0:
                temperature = None
        return temperature

    def str_to_int(self,str_temperature):
        try:
            return int(str_temperature)
        except (TypeError, ValueError):
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
