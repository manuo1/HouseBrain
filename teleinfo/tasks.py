import logging
from result import Err, Ok
from celery import shared_task
from teleinfo.teleinfo_listener import start_listener

logger = logging.getLogger("django")


@shared_task(bind=True)
def start_teleinfo_listener_task(self):
    """
    Tâche Celery qui démarre et maintient le listener Teleinfo en fonctionnement.
    """
    match start_listener():
        case Ok(listener):
            logger.info("[TeleinfoListener] Started")
            try:
                # Démarrer la boucle d'écoute
                listener.listen()
            except Exception as e:
                logger.error(f"[TeleinfoListener] Error in listener: {str(e)}")
                # S'assurer que le listener est arrêté proprement
                listener.stop()
        case Err(e):
            logger.error(e)
