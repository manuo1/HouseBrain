from django.core import management
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings

from housebrain_config.settings.messages import (
    HEATINGMODE_AUTO as auto,
    HEATINGMODE_MANUAL as manual,
    HEATING_PRIORITY,
    SETPOINT_TEMPERATURE
)

class RoomManager(models.Manager):

    def room(self, room_id):
        room = Room.objects.filter( id = room_id )
        if not room:
            room = [None]
        return room[0]

    def all_rooms(self):
        return Room.objects.all().order_by('heating_priority', 'name')

    def change_setpoint_temperature(self, room, temperature):
        if room.setpoint_temperature != temperature:
            room.setpoint_temperature = temperature
            room.save()

    def set_manual_temperature(self, room_id, manual_mode_data):
        room = self.room(room_id)
        room.manual_mode_start = manual_mode_data['manual_mode_start']
        room.manual_mode_end = manual_mode_data['manual_mode_end']
        room.manual_setpoint_temperature = manual_mode_data[
                'manual_setpoint_temperature'
            ]*1000
        room.save()

    def delete_manual_temperature(self, room):
        room.manual_mode_start = None
        room.manual_mode_end = None
        room.manual_setpoint_temperature = 20000
        room.save()

    def delete_manual_temperature_with_id(self, room_id):
        room = self.room(room_id)
        room.manual_mode_start = None
        room.manual_mode_end = None
        room.manual_setpoint_temperature = 20000
        room.save()

class Room(models.Model):

    name = models.CharField(max_length=100)
    heating_priority = models.IntegerField(default=100)
    manual_mode_start = models.DateTimeField(null=True, blank=True)
    manual_mode_end = models.DateTimeField(null=True, blank=True)
    manual_setpoint_temperature = models.IntegerField(default=20000)
    setpoint_temperature = models.IntegerField(default=5000)

    def __str__(self):
        return (
            f'{self.name} | '
            f'{HEATING_PRIORITY[settings.LANGUAGE_CODE]} : '
            f'{str(self.heating_priority)} | '
            f'{SETPOINT_TEMPERATURE[settings.LANGUAGE_CODE]} : '
            f'{str(self.setpoint_temperature)}'
        )
