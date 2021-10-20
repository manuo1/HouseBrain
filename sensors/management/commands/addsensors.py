from django.conf import settings
from housebrain_config.settings.constants import (
    DEBUG_SENSOR_FOLDER_PATHS,
    W1_DIRECTORY_PATH,
    TEMPERATURE_SENSORS_FAMILY_CODES,
)
import glob

from pathlib import Path
from django.core.management.base import BaseCommand
from sensors.models import TemperatureSensorManager

temperature_sensor_manager = TemperatureSensorManager()

class Command(BaseCommand):
    help = """
    Search and add sensors to the database.
    """

    def handle(self, *args, **options):
        """main controler."""
        temperature_sensor_manager.add_sensors(self.all_temperature_sensors())

    def all_temperature_sensors(self):
        """ Search temperature sensors """
        # add a false sensor_folder_paths in debug mode (no sensor connected)
        if settings.DEBUG:
            sensor_folder_paths = DEBUG_SENSOR_FOLDER_PATHS
            self.stdout.write("---- UNPLUGGED_MODE ----")
        else:
            sensor_folder_paths = []
            # On the Raspberry
            #| Data from one_wire sensors are stored in a folder where each
            #| sub-folder name begins with the sensor's family code
            # glob module finds all the pathname matching a specified pattern
            for family_code in TEMPERATURE_SENSORS_FAMILY_CODES:
                sensor_folder_paths.extend(
                    glob.glob(f'{Path(W1_DIRECTORY_PATH)}/{family_code}*')
                )
        for path in sensor_folder_paths:
            self.stdout.write(path)
        self.stdout.write(f'{len(sensor_folder_paths)} sensors found ')

        return sensor_folder_paths
