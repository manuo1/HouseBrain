from django.core import management
from django.core.management.base import BaseCommand

from rooms.models import RoomManager
from heating_manager.models import HeatingPeriodManager

heating_period_manager = HeatingPeriodManager()
room_manager = RoomManager()

class Command(BaseCommand):

    help = """
    will change the state of the heater of each room
    according the temperatures and remaining intensity
    """
    def add_arguments(self, manage_heating_periods):
        pass

    def handle(self, *args, **options):
        for room in room_manager.all_rooms():
            room_manager.change_setpoint_temperature(
                room,
                heating_period_manager.current_heating_period_setpoint_temperature(room)
            )
        management.call_command('manage_heaters')
