import logging
from django.db import models
from core.constants import DEFAULT_VOLTAGE, UNPLUGGED_MODE
from core.services import watt_to_ampere
from heating_control.constants import VERY_HIGH_INTENSITY, HeatingMode
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
    def toggle_radiators_state(
        cls,
        radiators_to_turn_on: list["Radiator"],
        radiators_to_turn_off: list["Radiator"],
    ) -> int:
        radiators_updated = 0

        try:
            allow_heating_without_teleinfo = (
                UserSettings.objects.last().allow_heating_without_teleinfo
            )
        except AttributeError:
            allow_heating_without_teleinfo = False

        if allow_heating_without_teleinfo:
            for radiator in [*radiators_to_turn_on, *radiators_to_turn_off]:
                radiator.is_on = not radiator.is_on
                radiator.save()
                radiators_updated += 1
        else:
            match get_last_available_intensity():
                case Ok(available_intensity):
                    logger.info(
                        f"Available intensity = {available_intensity}A - {type(available_intensity)}"
                    )
                case Err(e):
                    available_intensity = 0
                    logger.error(e)

            recovered_power = sum(radiator.power for radiator in radiators_to_turn_off)

            match watt_to_ampere(recovered_power, DEFAULT_VOLTAGE):
                case Ok(recovered_intensity):
                    pass
                case Err(e):
                    logger.error(e)
                    recovered_intensity = 0

            available_intensity += recovered_intensity

            # Pour allumer les radiateurs prioritaires en premier
            sorted_radiators_to_turn_on = sorted(
                radiators_to_turn_on, key=lambda r: r.priority
            )

            for radiator in [*radiators_to_turn_off, *sorted_radiators_to_turn_on]:
                if not radiator.power:
                    logger.error(
                        f"[Heating Control] Radiator's power is not set, it will never be updated {radiator}"
                    )
                    continue

                match watt_to_ampere(radiator.power, DEFAULT_VOLTAGE):
                    case Ok(radiator_intensity):
                        pass
                    case Err(e):
                        logger.error(e)
                        radiator_intensity = VERY_HIGH_INTENSITY

                if radiator.is_on:
                    radiator.is_on = False
                    radiator.save()
                    radiators_updated += 1

                elif not radiator.is_on and available_intensity > radiator_intensity:
                    available_intensity -= radiator_intensity
                    radiator.is_on = True
                    radiator.save()
                    radiators_updated += 1
                else:
                    logger.warning(
                        f"[Heating Control] Unable to turn on radiator {radiator}, not enough intensity available"
                    )
                    break

        return radiators_updated

    @classmethod
    def in_manual_heating_home_zone(cls):
        return list(cls.objects.filter(homezone__heating_mode=HeatingMode.MANUAL))

    @classmethod
    def in_off_heating_home_zone(cls):
        return list(cls.objects.filter(homezone__heating_mode=HeatingMode.OFF))
