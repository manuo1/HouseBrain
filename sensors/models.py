from django.db import models, IntegrityError
from rooms.models import Room

class TemperatureSensorManager(models.Manager):
    def add_sensors(self, sensor_folder_paths):
        for path in sensor_folder_paths:
            temperature_sensor = TemperatureSensor(sensor_folder_path = path)
            try:
                temperature_sensor.save()
            except IntegrityError:
                pass

class TemperatureSensor(models.Model):

    name = models.CharField(
        default="unnamed",
        max_length=100
    )
    sensor_folder_path = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
    )
    associated_room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
         blank=True,
         null=True,
    )

    def __str__(self):
	       return self.name

class TemperatureHistory(models.Model):
    temperature = models.DecimalField(
        default=99.9,
        max_digits=3,
        decimal_places=1
    )
    date = models.DateTimeField(
        auto_now_add=True
    )
    associated_sensor = models.ForeignKey(
        TemperatureSensor,
        on_delete=models.CASCADE
    )
