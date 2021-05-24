from sensors.models import TemperatureSensorManager

from django.core.management.base import BaseCommand

temperature_sensor_manager = TemperatureSensorManager()

class Command(BaseCommand):
    help = """
    will save all current temperatures
    """

    def add_arguments(self, get_all_current_temperatures):
        pass

    def handle(self, *args, **options):
        """main controler."""
        for sensor in temperature_sensor_manager.all_sensor_list():
            temperature_sensor_manager.save_temperature(
                self.read_temperature(sensor),
                sensor
            )

    def read_temperature(self, sensor):
        try:
            with open (sensor.sensor_folder_path + "/temperature") as file:
                temperature = file.readline()[:-1] #[:-1] to remove \n
        except FileNotFoundError:
            temperature = 99999
        return temperature
