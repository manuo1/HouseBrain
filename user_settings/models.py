from django.db import models


class UserSettings(models.Model):
    allow_heating_without_teleinfo = models.BooleanField(
        default=False,
        help_text="Autoriser l'allumage des radiateurs même si les données de téléinfo ne sont pas disponibles",
    )

    def __str__(self):
        return "Paramètres de l'application"
