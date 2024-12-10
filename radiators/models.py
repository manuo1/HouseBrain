import logging
from django.db import models
from contextlib import suppress
from core.constants import DEFAULT_VOLTAGE, UNPLUGGED_MODE
from core.services import watt_to_ampere
from heating_control.constants import RadiatorState
from radiators.mcp23017_control import set_mcp23017_pin_state
from result import Err, Ok

from teleinfo.services import get_last_available_intensity
from user_settings.models import UserSettings

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
        if UNPLUGGED_MODE:
            cls.objects.filter(is_on=True).update(is_on=False)
        else:
            # utiliser save ici est moins perf mais permet d'utiliser les contrôles
            # de la surcharge de save()
            for radiator in cls.objects.filter(is_on=True):
                radiator.is_on = False
                radiator.save()

    @classmethod
    def get_all_states(cls):
        return {
            radiator.name: {
                "state": "on" if radiator.is_on else "off",
                "power": radiator.power,
                "intensity": (
                    watt_to_ampere(radiator.power).unwrap()
                    if isinstance(watt_to_ampere(radiator.power, DEFAULT_VOLTAGE), Ok)
                    else 0
                ),
            }
            for radiator in Radiator.objects.all()
        }

    @classmethod
    def turn_on_or_off_radiators(cls, radiators_to_modify: list[RadiatorState]) -> int:
        updated = 0

        try:
            allow_heating_without_teleinfo = (
                UserSettings.objects.last().allow_heating_without_teleinfo
            )
        except UserSettings.DoesNotExist:
            allow_heating_without_teleinfo = False

        if allow_heating_without_teleinfo:
            for radiator_new_state in radiators_to_modify:
                with suppress(cls.DoesNotExist):
                    radiator = cls.objects.get(id=radiator_new_state.radiator_id)
                    radiator.is_on = radiator_new_state.is_on
                    radiator.save()
                    updated += 1
        else:
            # on éteint tous les radiateur à éteindre et
            # on allume les autres par ordre de priorité en respectant l'intensité maximum disponible

            match get_last_available_intensity():
                case Ok(available_intensity):
                    pass
                case Err(e):
                    available_intensity = 0
                    logger.error(e)

            # Trier avec is_on=False en premier, puis is_on=True trié par priority
            sorted_radiators_to_modify = sorted(
                radiators_to_modify,
                key=lambda r: (r.is_on, r.priority if r.is_on else 0),
            )

            for radiator_new_state in sorted_radiators_to_modify:
                with suppress(cls.DoesNotExist):
                    radiator = cls.objects.get(id=radiator_new_state.radiator_id)
                    match watt_to_ampere(radiator.power, DEFAULT_VOLTAGE):
                        case Ok(radiator_intensity):
                            pass
                        case Err(e):
                            logger.error(e)
                            radiator_intensity = 999999
                    if not radiator_new_state.is_on:
                        # si on doit éteindre un radiateur
                        # on rajoute son intensité à l'intensité disponible
                        available_intensity += radiator_intensity
                    elif (
                        radiator_new_state.is_on
                        and available_intensity > radiator_intensity
                    ):
                        available_intensity -= radiator_intensity
                    else:
                        logger.warning(
                            f"Radiator {radiator} not on to avoid load shedding"
                        )
                        continue
                    radiator.is_on = radiator_new_state.is_on
                    radiator.save()
                    updated += 1

        return updated
