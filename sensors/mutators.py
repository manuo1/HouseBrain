import logging
from result import Result, Ok, Err
from sensors.models import TemperatureHumiditySensor

logger = logging.getLogger("django")


def create_new_sensors(data: dict) -> Result[bool, str]:
    created = True
    try:
        mac_address = data["mac_address"]
    except KeyError:
        return Err(f"sensor don't have mac_address : {data}")

    name = data.get("name", "Unknown")

    _, created = TemperatureHumiditySensor.objects.get_or_create(
        mac_address=mac_address, defaults={"name": name}
    )
    if created:
        return Ok(created)
    else:
        return Ok(not created)
