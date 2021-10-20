import time
from django.utils import timezone
from django.conf import settings
from django.core.management.base import BaseCommand
from rooms.models import RoomManager
from sensors.models import TemperatureSensorManager
from heaters.models import HeaterManager
from teleinformation.models import TeleinfoManager
from housebrain_config.settings.constants import (
    MANAGE_HEATERS_TIMEOUT as timeout,
    HEATER_VOLTAGE as volts
)

room_manager = RoomManager()
temperature_sensor_manager = TemperatureSensorManager()
heater_manager = HeaterManager()
teleinfo_manager = TeleinfoManager()

class Command(BaseCommand):

    help = """
    will change the state of the heater of each room
    according the temperatures and remaining intensity
    """

    def handle(self, *args, **options):
        """main controler."""
        # turn off all heaters in rooms that do not need to be heated, and
        # | store those that do need to be heated in rooms_requiring_heating
        rooms_requiring_heating = []
        for room in self.rooms_with_heaters_and_sensor():
            if room["sensor"].is_malfunctioning:
                self.turn_off_the_room_heaters(room)
            else:
                temperature = self.temperature_level(room)
                # check if temperature is too low, too high or correct
                if temperature == "too low":
                    #try to turn on the rooms heaters
                    rooms_requiring_heating.append(room)
                elif temperature == "too high":
                    self.turn_off_the_room_heaters(room)
                else:
                    # if the temperature is correct check if the temperatures
                    # | increase, decrease or is stable
                    temperature = self.temperature_variation(room)
                    if temperature == "increasing":
                        self.turn_off_the_room_heaters(room)
                    elif temperature == "decreasing":
                        #try to turn on the rooms heaters
                        rooms_requiring_heating.append(room)
                    else:
                        pass
        # get the teleinformation remaining intensity
        usable_intensity = self.usable_intensity_measurement()
        # add the intensity of the heaters already on to know the total
        #   intensity available if all the heaters were off
        usable_intensity += self.intensity_of_heaters_already_on(rooms_requiring_heating)
        # check which rooms need to be heated can be heated with the available
        #|  intensity
        rooms_that_can_be_heated = self.rooms_that_can_be_heated(rooms_requiring_heating, usable_intensity)
        for room in rooms_that_can_be_heated:
            self.turn_on_the_room_heaters(room)


    def rooms_that_can_be_heated(self, rooms, usable_intensity):
        rooms_that_can_be_heated = []
        for room in rooms:
            if room["intensity"] < usable_intensity:
                rooms_that_can_be_heated.append(room)
                usable_intensity -= room["intensity"]
        return rooms_that_can_be_heated

    def intensity_of_heaters_already_on(self,rooms):
        intensity = 0
        for room in rooms:
            if room["heaters"][0].is_on:
                intensity += room["intensity"]
        return intensity

    def usable_intensity_measurement(self):
        intensity = 0
        previous = actual = teleinfo_manager.last_power_monitoring()
        timeout_start = time.time()
        # wait for a new power_monitoring measurement
        while actual.date_time == previous.date_time:
            # break if timout
            if time.time() > (timeout_start + timeout):
                break
            actual = teleinfo_manager.last_power_monitoring()
            time.sleep(0.5)
        # if the power monitoring measurement has changed
        if actual.date_time != previous.date_time:
            intensity = actual.ISOUSC - actual.IINST
        return intensity


    def rooms_with_heaters_and_sensor(self):
        rooms_with_heaters_and_sensor = []
        for room in room_manager.all_rooms():
            room_heaters = heater_manager.room_heaters(room)
            room_sensor = temperature_sensor_manager.room_sensor(room)
            if room_heaters and room_sensor:
                intensity = 0
                for heater in room_heaters:
                    intensity += heater.watts/volts
                room_data = {}
                room_data["room"] = room
                room_data["sensor"] = room_sensor
                room_data["heaters"] = list(room_heaters)
                room_data["intensity"] = intensity
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
