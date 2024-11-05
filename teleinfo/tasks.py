import logging
from result import Err, Ok
from celery import shared_task
from teleinfo.teleinfo_listener import start_listener

logger = logging.getLogger("django")


@shared_task(bind=True)
def start_teleinfo_listener_task(self):
    match start_listener():
        case Ok(listener):
            logger.info("[TeleinfoListener] Started")
            try:
                listener.listen()
            except Exception as e:
                logger.error(f"[TeleinfoListener] Error in listener: {str(e)}")
                listener.stop()
        case Err(e):
            logger.error(e)
