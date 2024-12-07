from django.db import models

from radiators.models import Radiator
from sensors.models import TemperatureHumiditySensor


class HomeZone(models.Model):
    HEATING_MODES = [
        ("manual", "Manual"),
        ("auto", "Automatic"),
        ("off", "Off"),
    ]
    HEATING_EFFICIENCY_CORRECTION_MODE = [
        ("manual", "Manual"),
        ("auto", "Automatic"),
    ]

    name = models.CharField(max_length=100, unique=True)
    temperature_humidity_sensor = models.ForeignKey(
        TemperatureHumiditySensor, on_delete=models.SET_NULL, null=True, blank=True
    )
    radiator = models.ForeignKey(
        Radiator, on_delete=models.SET_NULL, null=True, blank=True
    )
    heating_mode = models.CharField(max_length=10, choices=HEATING_MODES, default="off")
    target_temperature = models.FloatField(null=True, blank=True)
    heating_efficiency = models.PositiveIntegerField(
        default=100,
        help_text=(
            "< 100 % = piece longue à chauffer  |  > 100 % = piece rapide à chauffer"
        ),
    )
    heating_efficiency_correction_mode = models.CharField(
        max_length=10,
        choices=HEATING_EFFICIENCY_CORRECTION_MODE,
        default="auto",
        help_text=(
            "heating_efficiency sera ajusté automatiquement sauf en mode manuel"
        ),
    )

    def __str__(self):
        return self.name
