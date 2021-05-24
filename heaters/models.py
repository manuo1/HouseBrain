from django.db import models
from rooms.models import Room

class Heater(models.Model):

    name = models.CharField(max_length=100)
    maximum_power_consumption = models.IntegerField()
    control_pin = models.IntegerField(unique=True)
    is_on = models.BooleanField(default=False)
    associated_room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
         blank=True,
         null=True,
        )

    def __str__(self):
	       return self.name
