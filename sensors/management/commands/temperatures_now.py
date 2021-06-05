from django.conf import settings
from django.utils import timezone
from housebrain_config.settings.constants import (
    DEBUG_TEMPERATURE,
    ERROR_TEMPERATURE,
    TEMPERATURE_FILE
)
from sensors.models import TemperatureSensorManager
from django.core.management.base import BaseCommand

temperature_sensor_manager = TemperatureSensorManager()

class Command(BaseCommand):
    help = """
    will save in database all temperature sensors current temperatures
    """
    def add_arguments(self, temperatures_now):
        pass

    def handle(self, *args, **options):
        """main controler."""
        for sensor in temperature_sensor_manager.all_sensors():
            temperature_sensor_manager.save_temperature(
                self.read_temperature(sensor),
                sensor
            )

    def read_temperature(self, sensor):
        if settings.UNPLUGGED_MODE:
            temperature = DEBUG_TEMPERATURE
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
                self.stdout.write(
                    f"""
                    {f'{timezone.now():%d/%m/%Y %H:%M}'}
                     - temperature reading error, cannot find path
                    {sensor.sensor_folder_path + TEMPERATURE_FILE}
                    """
                )
                # increments the sensor error counter
                temperature_sensor_manager.add_an_error(sensor)

        return temperature
