from datetime import datetime
from result import Err, Ok, Result
from teleinfo.models import TeleinformationHistory


def get_last_teleinfo_created_datetime() -> Result[datetime, str]:
    try:
        return Ok(TeleinformationHistory.objects.latest("created").created)
    except TeleinformationHistory.DoesNotExist as e:
        return Err(e)
