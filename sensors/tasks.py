import logging
from celery import shared_task
from sensors.bluetooth_reading import get_bluetooth_bthome_th_sensors_data
from sensors.mutators import (
    create_new_sensors,
    invalidate_stale_measurements,
    update_temperature_and_humidity_values,
)
from result import Err, Ok
from core.celery import app
from celery.schedules import crontab


logger = logging.getLogger("django")


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute="*/5"),
        scan_and_update_bluetooth_bthome_th_sensors.s(),
    )


@shared_task
def scan_and_update_bluetooth_bthome_th_sensors():
    sensors_data = get_bluetooth_bthome_th_sensors_data()

    match create_new_sensors(sensors_data):
        case Ok(created_amount):
            if created_amount:
                logger.info(f"{created_amount} sensor was created")
        case Err(e):
            logger.error(e)

    match update_temperature_and_humidity_values(sensors_data):
        case Ok(updated_amount):
            if updated_amount:
                logger.info(f"{updated_amount} sensor was updated")
        case Err(e):
            logger.error(e)

    match invalidate_stale_measurements():
        case Ok(stale_measurements_amount):
            if stale_measurements_amount:
                logger.warning(
                    f"{stale_measurements_amount} sensors have obsolete measurements"
                )
        case Err(e):
            logger.error(e)

    return f"{len(sensors_data)} sensors processed"
