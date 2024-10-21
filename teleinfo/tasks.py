import logging
from result import Err, Ok
from celery import shared_task
from teleinfo.teleinfo_listener import start_listener

logger = logging.getLogger("django")


@shared_task
def start_teleinfo_listener_task():
    match start_listener():
        case Ok(_):
            logger.info("[TeleinfoListener] Started")
        case Err(e):
            logger.error(e)
