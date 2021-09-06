from sensors.models import TemperatureSensorManager
from django.core.management.base import BaseCommand

temperature_sensor_manager = TemperatureSensorManager()

class Command(BaseCommand):
    help = """
    will delette all temperatures history
    """
    def add_arguments(self, temperatures_history_reset):
        pass

    def handle(self, *args, **options):
        """main controler."""
        temperature_sensor_manager.clear_all_temperature_history()
