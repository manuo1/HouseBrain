from django.conf import settings
#from housebrain_config.settings.constants import ()
from django.core.management.base import BaseCommand
from rooms.models import RoomManager
from sensors.models import TemperatureSensorManager
from heaters.models import HeaterManager

room_manager = RoomManager()
temperature_sensor_manager = TemperatureSensorManager()
heater_manager = HeaterManager()

class Command(BaseCommand):

    help = """
    will change the state of the heater of each room
    according the temperatures
    """
    def add_arguments(self, manage_heaters):
        pass

    def handle(self, *args, **options):
        """main controler."""
        for room in self.rooms_with_heaters_and_sensor():
            if room["sensor"].is_malfunctioning:
                self.turn_off_the_room_heaters(room)
            else:
                temperature = self.temperature_level(room)
                # check if temperature is too low, too high or correct
                if temperature == "too low":
                    self.turn_on_the_room_heaters(room)
                elif temperature == "too high":
                    self.turn_off_the_room_heaters(room)
                else:
                    # if the temperature is correct check if the temperatures
                    # | increase, decrease or is stable
                    temperature = self.temperature_variation(room)
                    if temperature == "increasing":
                        self.turn_off_the_room_heaters(room)
                    elif temperature == "decreasing":
                        self.turn_on_the_room_heaters(room)
                    else:
                        pass

    def rooms_with_heaters_and_sensor(self):
        rooms_with_heaters_and_sensor = []
        for room in room_manager.all_rooms():
            room_heaters = heater_manager.room_heaters(room)
            room_sensor = temperature_sensor_manager.room_sensor(room)
            if room_heaters and room_sensor:
                room_data = {}
                room_data["room"] = room
                room_data["sensor"] = room_sensor
                room_data["heaters"] = list(room_heaters)
                rooms_with_heaters_and_sensor.append(room_data)
        return rooms_with_heaters_and_sensor

    def temperature_level(self, room):
        temperature_level = ""
        delta = (room["sensor"].last_measured_temperature -
            room["room"].setpoint_temperature
        )
        if delta > 0:
            temperature_level = "too high"
        elif delta < 0:
            temperature_level = "too low"
        else:
            temperature_level = "correct"
        return temperature_level

    def temperature_variation(self,room):
        temperature_variation = ""
        delta = ( room["sensor"].last_measured_temperature -
            room["sensor"].previous_measured_temperature
        )
        if delta > 0:
            temperature_variation = "increasing"
        elif delta < 0:
            temperature_variation = "decreasing"
        else:
            temperature_variation = "stable"
        return  temperature_variation

    def turn_off_the_room_heaters(self, room):
        for heater in room["heaters"]:
            if heater.is_on:
                heater_manager.turn_off(heater)

    def turn_on_the_room_heaters(self, room):
        for heater in room["heaters"]:
            # need to add power remaining check
            if not heater.is_on:
                heater_manager.turn_on(heater)
