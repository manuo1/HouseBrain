from django.core.management.base import BaseCommand
from heaters.models import HeaterManager

heater_manager = HeaterManager()

class Command(BaseCommand):
    help = """
    will turn off all heaters
    """
    def add_arguments(self, turn_off_all_heaters):
        pass

    def handle(self, *args, **options):
        heater_manager.turn_off_all_heaters()
