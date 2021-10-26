from django.core import management
from django.core.management.base import BaseCommand
from django.utils import timezone

from rooms.models import RoomManager
from heating_manager.models import HeatingPeriodManager

heating_period_manager = HeatingPeriodManager()
room_manager = RoomManager()

class Command(BaseCommand):

    help = """
    will apply setpoints temperatures to each room
    """

    def handle(self, *args, **options):
        for room in room_manager.all_rooms():
            # get automatic room setpoint temperature
            setpoint_temperature = (
                heating_period_manager.
                current_heating_period_setpoint_temperature(room)
            )
            # delete manual temperatures data if manual_mode_end is exceeded
            if room.manual_mode_end:
                if timezone.now() >= room.manual_mode_end:
                    room_manager.delete_manual_temperature(room)
            # get manual room setpoint temperatures if exist
            if room.manual_mode_end:
                if room.manual_mode_start <= timezone.now() <= room.manual_mode_end:
                    setpoint_temperature = room.manual_setpoint_temperature
            # apply new room setpoint temperature
            room_manager.change_setpoint_temperature(
                room,
                setpoint_temperature
            )
