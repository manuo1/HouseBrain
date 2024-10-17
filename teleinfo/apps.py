import logging
import threading
from django.apps import AppConfig
from result import Err, Ok
from django.db.models.signals import post_migrate

from teleinfo.constants import TELEINFO_LISTENER_THREAD_NAME

logger = logging.getLogger("django")


def start_listener_after_migrations(sender, **kwargs):
    from teleinfo.teleinfo_listener import start_listener

    logger.info("[TeleinfoListener] Initializing...")
    match start_listener():
        case Ok(listener):
            for thread in threading.enumerate():
                if thread.name == TELEINFO_LISTENER_THREAD_NAME:
                    logger.info(
                        f"[TeleinfoListener] {TELEINFO_LISTENER_THREAD_NAME} thread started"
                    )
            if listener.running:
                logger.info("[TeleinfoListener] Teleinfo listener is running.")
        case Err(e):
            logger.error(e)


class TeleinfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teleinfo"

    def ready(self):
        # start listener after migrations
        post_migrate.connect(start_listener_after_migrations, sender=self)
