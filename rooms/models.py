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

    def all_rooms(self):
        return Room.objects.all().order_by('heating_priority', 'name')

class Room(models.Model):

    class HeatingModeChoices(models.IntegerChoices):
        AUTO = 0, auto[settings.LANGUAGE_CODE]
        MANUAL = 1, manual[settings.LANGUAGE_CODE]

    name = models.CharField(max_length=100)
    heating_priority = models.IntegerField(default=100)
    heating_mode = models.IntegerField(
        default=HeatingModeChoices.AUTO,
        choices=HeatingModeChoices.choices
        )
    setpoint_temperature = models.IntegerField(default=5000)

    def __str__(self):
        ret = "{} | {} : {} | {} : {} | mode : {}".format(
            self.name ,
            HEATING_PRIORITY[settings.LANGUAGE_CODE],
            str(self.heating_priority),
            SETPOINT_TEMPERATURE[settings.LANGUAGE_CODE],
            str(self.setpoint_temperature),
            str(self.HeatingModeChoices.choices[self.heating_mode][1])
        )
        return ret

"""
    django.db.models.signals.post_save
    Use Django signals sent at the end of a model’s save() method.
    Every change on Room objects will run manage_heaters commande
    to update room heaters state
"""
def update_room_heaters_state(sender, instance, created, **kwargs):
    management.call_command('manage_heaters')
post_save.connect(update_room_heaters_state, sender=Room)
