import logging
from celery import shared_task
from sensors.bluetooth_reading import get_bluetooth_bthome_th_sensors_data
from sensors.mutators import create_new_sensors
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
    sensors_data = get_bluetooth_bthome_th_sensors_data(scan_duration=10)
    for _, data in sensors_data.items():
        match create_new_sensors(data):
            case Ok(created):
                if created:
                    logger.info(f"New sensor was added {data}")
            case Err(e):
                logger.error(e)

    return f"{len(sensors_data)} sensors processed"
