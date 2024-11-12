import logging
from load_shedding.models import ElectricityDemandExceedance
from radiators.models import Radiator
from result import Err, Ok
from teleinfo.constants import Teleinfo
from teleinfo.services import get_available_intensity

logger = logging.getLogger("django")


def manage_load_shedding(teleinfo: Teleinfo) -> None:
    """coupe les chauffages en cas de dépassement de puissance"""
    match get_available_intensity(teleinfo):
        case Ok(available_intensity):
            if available_intensity <= 0:
                Radiator.turn_off_all()
                ElectricityDemandExceedance.save_exceedance(teleinfo)
        case Err(e):
            logger.error(e)
