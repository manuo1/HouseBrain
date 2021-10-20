from teleinformation.models import TeleinfoManager
from django.core.management.base import BaseCommand

teleinfo_manager = TeleinfoManager()

class Command(BaseCommand):
    help = """
    will delette all Teleinformation history
    """

    def handle(self, *args, **options):
        """main controler."""
        teleinfo_manager.delete_all_teleinformation_history()
