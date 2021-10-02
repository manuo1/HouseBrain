from django.conf import settings
from django.utils import timezone
from housebrain_config.settings.constants import (
    MAX_TEMPERATURE as max_temp,
    MIN_TEMPERATURE as min_temp,
    MAX_DELTA_TEMPERATURE as max_delta,
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
            new_temperature = self.read_temperature(sensor)
            if self.temperature_is_valid(new_temperature, sensor):
                sensor_manager.save_temperature(
                    new_temperature, sensor
                )
            else:
                sensor_manager.add_an_error(sensor)

        if self.it_s_time_to_save_temperature_history():
            sensor_manager.save_temperature_history()

    def it_s_time_to_save_temperature_history(self):
        return timezone.now().minute % TEMPERATURE_HISTORY_DELTA == 0

    def read_temperature(self, sensor):
        if settings.UNPLUGGED_MODE:
            temperature = DEBUG_TEMPERATURE
            self.stdout.write("reading temp in ---- UNPLUGGED_MODE ----")
        else :
            try:
                with open (
                    sensor.sensor_folder_path + TEMPERATURE_FILE
                ) as file:
                    lines = file.readlines()
                    if len(lines) >= 2:
                        line_1_split = lines[0].split()
                        crc="NO"
                        if line_1_split:
                            crc=line_1_split[-1]
                        if crc == "YES":
                            temperature = lines[1].split()[-1][2:]
                            try:
                                temperature = int(temperature)
                            except ValueError:
                                temperature = ERROR_TEMPERATURE
                                sensor_manager.add_an_error(sensor)
                        else:
                            temperature = ERROR_TEMPERATURE
                            sensor_manager.add_an_error(sensor)
            except FileNotFoundError:
                temperature = ERROR_TEMPERATURE
                sensor_manager.add_an_error(sensor)
        print(temperature)
        return temperature

    def temperature_is_valid(self, new_temperature, sensor):
        is_valid = True
        # check if new_temperature is between possible max an min temperatures
        if (new_temperature > max_temp or new_temperature < min_temp):
            is_valid = False
        # check if there is not too much difference between the new one and
        #| the previous measurement (does not check this condition if the
        #| sensor has just been created, when creating the sensor,
        #| last_temperature = ERROR_TEMPERATURE)
        last_temperature = sensor.last_measured_temperature
        delta_temp = abs(last_temperature - new_temperature)
        if (last_temperature != ERROR_TEMPERATURE and delta_temp > max_delta):
            is_valid = False
        return is_valid
