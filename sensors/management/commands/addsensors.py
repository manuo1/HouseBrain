
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
        # Raspberry have folder with alls one wire devices at W1_DIRECTORY
        W1_DIRECTORY = Path("/sys/bus/w1/devices")
        # The data of each of the one-wire sensors is stored in files named by
        # |     the sensor address and the DS18B20 sensors address start with
        # |     the number 28
        # glob module finds all the pathnames matching a specified pattern
        sensor_folder_paths = glob.glob(str(W1_DIRECTORY)+"/28*")
        sensor_folder_paths = ['/sys/bus/w1/devices/28-000005c7cc82', '/sys/bus/w1/devices/28-000005c83f61', '/sys/bus/w1/devices/28-000005c7d98e', '/sys/bus/w1/devices/28-000005c6f49f', '/sys/bus/w1/devices/28-000005c83686', '/sys/bus/w1/devices/28-000005c6d2aa', '/sys/bus/w1/devices/28-000005c7824f', '/sys/bus/w1/devices/28-000005c6d680']
        return sensor_folder_paths
