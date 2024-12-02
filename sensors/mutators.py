import logging
from result import Result, Ok, Err
from sensors.models import TemperatureHumiditySensor
from django.utils import timezone

logger = logging.getLogger("django")


def create_new_sensors(sensors_data: dict) -> Result[int, str]:

    if not isinstance(sensors_data, dict):
        return Err("Invalid input: new_sensors_data must be a dict")

    known_sensors_mac_address = TemperatureHumiditySensor.objects.values_list(
        "mac_address", flat=True
    )

    valid_sensors = [
        (data["mac_address"], data.get("name", "Unknown"))
        for _, data in sensors_data.items()
        if isinstance(data, dict)
        and data.get("mac_address")
        and data["mac_address"] not in known_sensors_mac_address
    ]

    new_sensors = [
        TemperatureHumiditySensor(mac_address=mac_address, name=name)
        for mac_address, name in valid_sensors
    ]

    created = TemperatureHumiditySensor.objects.bulk_create(new_sensors)

    return Ok(len(created))


def update_temperature_and_humidity_values(sensors_data: dict) -> Result[int, str]:

    if not isinstance(sensors_data, dict):
        return Err("Invalid input: new_sensors_data must be a dict")

    sensors_updated_amount = 0
    for _, data in sensors_data.items():
        try:
            affected_rows = TemperatureHumiditySensor.objects.filter(
                mac_address=data["mac_address"]
            ).update(
                temperature=data["temperature"],
                humidity=data["humidity"],
                rssi=data["rssi"],
                last_update=timezone.now(),
            )
            sensors_updated_amount += affected_rows
        except KeyError:
            logger.error(f"Incorrects temperature humidity sensor data{data}")
    return Ok(sensors_updated_amount)
