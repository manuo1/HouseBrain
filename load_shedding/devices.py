import logging
from radiators.models import Radiator
from result import Err, Ok, Result
from teleinfo.constants import Teleinfo

logger = logging.getLogger("django")


def get_available_current(teleinfo: Teleinfo) -> Result[(int, int), str]:
    try:
        return int(teleinfo.data["ISOUSC"]) - int(teleinfo.data["IINST"])
    except KeyError:
        return Err("Missing IINST or ISOUSC in teleinfo data")
    except ValueError:
        return Err("Invalid value for IINST or ISOUSC")


def manage_load_shedding(teleinfo: Teleinfo) -> None:
    """coupe les chauffages en cas de dépassement de puissance"""
    match get_available_current(teleinfo):
        case Ok(available_current):
            if available_current <= 0:
                Radiator.turn_off_all()
        case Err(e):
            logger.error(e)
