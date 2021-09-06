from teleinformation.models import TeleinfoManager
from django.core.management.base import BaseCommand

teleinfo_manager = TeleinfoManager()

class Command(BaseCommand):
    help = """
    will delette all Teleinformation history
    """
    def add_arguments(self, teleinfo_history_reset):
        pass

    def handle(self, *args, **options):
        """main controler."""
        teleinfo_manager.clear_all_teleinformation_history()
