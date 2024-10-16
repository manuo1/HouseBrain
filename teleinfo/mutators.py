from datetime import datetime
from django.utils import timezone
import logging
from result import Err, Ok, Result
from teleinfo.models import TeleinformationHistory
from teleinfo.selectors import get_last_teleinfo_created_datetime
from teleinfo.services import is_new_hour
from teleinfo.teleinfo_listener import Teleinfo

logger = logging.getLogger(__name__)


def save_teleinfo(teleinfo: Teleinfo) -> Result[bool, str]:
    saved = True
    if not teleinfo.last_save:
        # récupère le last_save en bdd
        match get_last_teleinfo_created_datetime():
            case Ok(last_teleinfo_dt):
                teleinfo.last_save = last_teleinfo_dt
            case Err(_):
                teleinfo.last_save = datetime.min.replace(
                    tzinfo=timezone.get_current_timezone()
                )
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
