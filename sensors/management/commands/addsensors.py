from django.conf import settings
from housebrain_config.settings.constants import (
    DEBUG_SENSOR_FOLDER_PATHS,
    W1_DIRECTORY_PATH
)
import glob

from pathlib import Path
from django.core.management.base import BaseCommand
from sensors.models import TemperatureSensorManager

temperature_sensor_manager = TemperatureSensorManager()

class Command(BaseCommand):
    help = """
    Search and add sensors to the database.
    (only those which do not already exist will be added)
    """

    def add_arguments(self, addsensors):
        pass

    def handle(self, *args, **options):
        """main controler."""
        temperature_sensor_manager.add_sensors(self.all_temperature_sensors())

    def all_temperature_sensors(self):
        """ Search temperature sensors """
        # Raspberry have folder with alls one wire devices at w1_directory
        # | set in : housebrain_config.settings.constants
        w1_directory = Path(W1_DIRECTORY_PATH)
        # The data of each of the one-wire sensors is stored in files named by
        # |     the sensor address and the DS18B20 sensors address start with
        # |     the number 28
        # glob module finds all the pathnames matching a specified pattern
        sensor_folder_paths = glob.glob(str(w1_directory)+"/28*")
        # add a false sensor_folder_paths in debug mode (no sensor connected)
        if settings.DEBUG:
            sensor_folder_paths = DEBUG_SENSOR_FOLDER_PATHS
        return sensor_folder_paths
