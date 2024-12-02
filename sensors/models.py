from django.db import models


class TemperatureHumiditySensor(models.Model):
    mac_address = models.CharField(
        max_length=17, unique=True, help_text="Adresse MAC du capteur"
    )
    name = models.CharField(max_length=100, blank=True, help_text="Nom du capteur")
    created_at = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField(
        null=True, blank=True, help_text="Température mesurée (en °C)"
    )
    humidity = models.FloatField(
        null=True, blank=True, help_text="Humidité mesurée (%)"
    )
    rssi = models.IntegerField(
        null=True,
        blank=True,
        help_text="Puissance du signal RSSI mesurée en dBm",
    )
    last_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date et heure de la dernière mise à jour des données",
    )

    def __str__(self):
        return f"{self.mac_address} - {self.name or 'Unnamed Sensor'}"
