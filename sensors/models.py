from django.db import models
from rooms.models import Room

class TemperatureSensor(models.Model):

    name = models.CharField(max_length=100)
    address = models.IntegerField(unique=True)
    last_measured_temperature = models.DecimalField(
        default=99.9,
        max_digits=3,
        decimal_places=1
        )
    previous_measured_temperature = models.DecimalField(
        default=99.9,
        max_digits=3,
        decimal_places=1
        )
    associated_room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
         blank=True,
         null=True,
        )

    def __str__(self):
	       return self.name
