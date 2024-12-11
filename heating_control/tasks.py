import logging
from celery import shared_task
from core.celery import app
from celery.schedules import crontab

from heating_control.constants import HeatingMode
from radiators.models import Radiator


logger = logging.getLogger("django")


@app.on_after_finalize.connect
def setup_on_start(**kwargs):
    Radiator.turn_off_all()
    logger.info("[Heating Control] All the radiators were turned off")


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute="*/1"), heating_control.s())


@shared_task
def heating_control():
    radiators_to_turn_on = []
    radiators_to_turn_off = []
    radiators = Radiator.with_heating_mode_home_zone()
    radiators_to_turn_on.extend(
        [r for r in radiators if not r.is_on and r.heating_mode == HeatingMode.MANUAL]
    )
    radiators_to_turn_off.extend(
        [r for r in radiators if r.is_on and r.heating_mode == HeatingMode.OFF]
    )

    # TODO implementer le chauffage en auto

    radiators_on = Radiator.toggle_radiators_state(
        radiators_to_turn_on, radiators_to_turn_off
    )

    return f"[Heating Control] task ok, {radiators_on} radiators Updated"
