from django.db import models
from django.conf import settings

from housebrain_config.settings.messages import (
    HEATINGMODE_AUTO as auto,
    HEATINGMODE_MANUAL as manual,
    HEATING_PRIORITY,
    SETPOINT_TEMPERATURE
)

class Room(models.Model):

    class HeatingModeChoices(models.IntegerChoices):
        AUTO = 0, auto[settings.LANGUAGE_CODE]
        MANUAL = 1, manual[settings.LANGUAGE_CODE]

    name = models.CharField(max_length=100)
    heating_priority = models.IntegerField(default=1)
    heating_mode = models.IntegerField(
        default=HeatingModeChoices.AUTO,
        choices=HeatingModeChoices.choices
        )
    setpoint_temperature = models.IntegerField(default=5)

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
