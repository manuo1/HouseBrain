from django.db import models


class TemperatureHumiditySensor(models.Model):
    mac_address = models.CharField(
        max_length=17, unique=True, help_text="Adresse MAC du capteur"
    )
    name = models.CharField(max_length=100, blank=True, help_text="Nom du capteur")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mac_address} - {self.name or 'Unnamed Sensor'}"
