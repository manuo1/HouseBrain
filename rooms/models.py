from django.db import models

class Room(models.Model):

    class HeatingModeChoices(models.IntegerChoices):
        AUTO = 1, 'Auto'
        MANUAL = 2, 'Manual'

    name = models.CharField(max_length=100)
    heating_priority = models.IntegerField(default=1)
    heating_mode = models.IntegerField(
        default=HeatingModeChoices.AUTO,
        choices=HeatingModeChoices.choices
        )
    setpoint_temperature = models.IntegerField(default=5)

    def __str__(self):
        ret = (
            self.name +
            " | priority " +
            str(self.heating_priority) +
            " | mode : " +
            str(self.heating_mode) +
            " | setpoint_temperature : " +
            str(self.setpoint_temperature) + "°C"
        )
        return ret
