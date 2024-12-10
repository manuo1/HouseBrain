import logging
from celery import shared_task
from result import Err, Ok
from core.celery import app
from celery.schedules import crontab

from homezones.selectors import get_non_auto_home_zones_radiators_states
from radiators.models import Radiator
from radiators.services import remove_the_unchanged_radiator


logger = logging.getLogger("django")


@app.on_after_finalize.connect
def setup_on_start(**kwargs):
    Radiator.turn_off_all()
    logger.info("All the radiators were turned off")


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute="*/1"), heating_control.s())


@shared_task
def heating_control():
    radiators_with_states = []
    match get_non_auto_home_zones_radiators_states():
        case Ok(non_auto_radiators_with_states):
            radiators_with_states.extend(non_auto_radiators_with_states)
        case Err(e):
            logger.error(e)

    # TODO implementer le chauffage en auto

    match remove_the_unchanged_radiator(radiators_with_states):
        case Ok(radiators_to_modify):
            if radiators_to_modify:
                updated = Radiator.turn_on_or_off_radiators(radiators_to_modify)
        case Err(e):
            logger.error(e)

    return f"Heating control task ok, {updated} radiators updated"
