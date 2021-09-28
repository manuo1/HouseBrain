from django.conf import settings
from django.utils import timezone
from housebrain_config.settings.constants import (
    MAX_TEMPERATURE as max_temp,
    MIN_TEMPERATURE as min_temp,
    DEBUG_TEMPERATURE,
    ERROR_TEMPERATURE,
    TEMPERATURE_FILE,
    TEMPERATURE_HISTORY_DELTA,
)
from sensors.models import TemperatureSensorManager
from django.core.management.base import BaseCommand

temperature_sensor_manager = TemperatureSensorManager()

class Command(BaseCommand):
    help = """
    will save in database all temperature sensors current temperatures
    """
    def add_arguments(self, temperature_monitoring):
        pass

    def handle(self, *args, **options):
        """main controler."""
        for sensor in temperature_sensor_manager.all_sensors():
            if self.temperature_is_valid(self.read_temperature(sensor)):
                temperature_sensor_manager.save_temperature(
                    self.read_temperature(sensor),
                    sensor
                )
            else:
                temperature_sensor_manager.add_an_error(sensor)
                
        if timezone.now().minute % TEMPERATURE_HISTORY_DELTA == 0:
            temperature_sensor_manager.save_temperature_history()

    def read_temperature(self, sensor):
        if settings.UNPLUGGED_MODE:
            temperature = DEBUG_TEMPERATURE
            self.stdout.write("reading temp in ---- UNPLUGGED_MODE ----")
        else :
            try:
                with open (
                    sensor.sensor_folder_path + TEMPERATURE_FILE
                ) as file:
                    temperature = int(file.readline()[:-1]) #[:-1] remove \n
                # reset the consecutive measurement error counter
                temperature_sensor_manager.reset_consecutive_errors(sensor)
            except FileNotFoundError:
                # if there is a reading error returns the error temperature
                temperature = ERROR_TEMPERATURE
                # increments the sensor error counter
                temperature_sensor_manager.add_an_error(sensor)

        return temperature

    def temperature_is_valid(self, new_temperature):
        if new_temperature > max_temp or new_temperature < min_temp:
            return False
        return True
