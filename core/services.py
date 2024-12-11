from datetime import datetime
from result import Err, Ok, Result


def watt_to_ampere(power_watts, voltage) -> Result[float, str]:
    if not voltage:
        return Err("Unable to convert watt to ampere, Voltage can't be zero.")
    return Ok(power_watts / voltage)


def ampere_to_watt(intensity_ampere, voltage) -> Result[float, str]:
    if not voltage:
        return Err("Unable to convert ampere to watt, Voltage can't be zero.")

    return Ok(intensity_ampere * voltage)


def is_new_hour(old_datetime: datetime, new_datetime: datetime) -> Result[bool, str]:
    if not all(isinstance(var, datetime) for var in (old_datetime, new_datetime)):
        return Err("'old_datetime' and 'new_datetime' must be of type 'datetime'.")

    rounded_old_datetime = old_datetime.replace(minute=0, second=0, microsecond=0)
    rounded_new_datetime = new_datetime.replace(minute=0, second=0, microsecond=0)
    if rounded_new_datetime > rounded_old_datetime:
        return Ok(True)
    else:
        return Ok(False)
