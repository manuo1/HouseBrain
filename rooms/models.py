from django.db import models

class Room(models.Model):

    class HeatingModeChoices(models.IntegerChoices):
        AUTO = 1, 'Auto'
        MANUAL = 2, 'Manuel'

    name = models.CharField(max_length=100)
    heating_priority = models.IntegerField(unique=True)
    heating_mode = models.IntegerField(
        default=HeatingModeChoices.AUTO,
        choices=HeatingModeChoices.choices
        )

    def __str__(self):
        return self.name
