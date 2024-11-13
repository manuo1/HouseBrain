import logging
from core.services import is_new_hour
from result import Err, Ok, Result
from teleinfo.models import TeleinformationHistory
from teleinfo.teleinfo_listener import Teleinfo


logger = logging.getLogger("django")


def save_teleinfo(teleinfo: Teleinfo) -> Result[bool, str]:
    saved = True

    match is_new_hour(teleinfo.last_save, teleinfo.created):
        case Ok(created_is_new_hour):
            if not created_is_new_hour:
                return
            else:
                pass
        case Err(e):
            logger.error(e)
            return

    _, created = TeleinformationHistory.objects.get_or_create(
        created=teleinfo.created.replace(second=0, microsecond=0),
        defaults={"data": teleinfo.data},
    )
    if created:
        return Ok(saved)
    else:
        return Ok(not saved)
