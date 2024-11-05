import logging
from django.db import models

from radiators.mcp23017_control import set_mcp23017_pin_state
from result import Err, Ok
from teleinfo.constants import UNPLUGGED_MODE

logger = logging.getLogger("django")


class Radiator(models.Model):
    MCP23017_PIN_CHOICES = [(pin, f"Pin {pin}") for pin in range(16)]

    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    power = models.PositiveIntegerField(verbose_name="Puissance (W)")
    control_pin = models.PositiveSmallIntegerField(
        choices=MCP23017_PIN_CHOICES,
        unique=True,
        verbose_name="Pin MCP23017",
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name="Priorité de délestage",
        help_text="Plus la valeur est basse, plus la priorité est élevée pour rester allumé.",
    )
    is_on = models.BooleanField(default=False, verbose_name="Allumé")
    error = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({'On' if self.is_on else 'Off'})"

    def save(self, *args, **kwargs):
        if not UNPLUGGED_MODE:
            # ajout nouveau radiateur
            if not self.pk:
                previous_state = False
            # Mise à jour d'un radiateur
            else:
                previous_state = Radiator.objects.get(pk=self.pk).is_on

            match set_mcp23017_pin_state(self.control_pin, self.is_on):
                case Ok(radiator_state):
                    if radiator_state == self.is_on:
                        self.error = ""
                    else:
                        self.is_on = radiator_state
                        self.error = "L'état du pin du MCP23017 n'a pas réussi à changer pour une raison inconnue"
                        logger.error(self.error)
                case Err(e):
                    self.is_on = previous_state
                    logger.error(e)
                    self.error = e
        super().save(*args, **kwargs)

    @classmethod
    def turn_off_all(cls):
        """
        Éteindre tous les radiateurs.
        """
        if UNPLUGGED_MODE:
            cls.objects.filter(is_on=True).update(is_on=False)
        else:
            # utiliser save ici est moins perf mais permet d'utiliser les contrôles
            # de la surcharge de save()
            for radiator in cls.objects.filter(is_on=True):
                radiator.is_on = False
                radiator.save()
