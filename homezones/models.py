from django.db import models

from radiators.models import Radiator
from sensors.models import TemperatureHumiditySensor


class HomeZone(models.Model):
    HEATING_MODES = [
        ("manual", "Manual"),
        ("auto", "Automatic"),
        ("off", "Off"),
    ]

    name = models.CharField(max_length=100, unique=True)
    temperature_humidity_sensor = models.ForeignKey(
        TemperatureHumiditySensor, on_delete=models.SET_NULL, null=True, blank=True
    )
    radiator = models.ForeignKey(
        Radiator, on_delete=models.SET_NULL, null=True, blank=True
    )
    target_temperature = models.FloatField(null=True, blank=True)
    heating_mode = models.CharField(max_length=10, choices=HEATING_MODES, default="off")

    def __str__(self):
        return self.name
