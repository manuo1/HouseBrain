import logging
from django.apps import AppConfig
from teleinfo.teleinfo_listener import start_listener

logger = logging.getLogger(__name__)


class TeleinfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teleinfo"

    def ready(self):
        logger.info("Starting Teleinfo listener")
        listener = start_listener()
        if listener:
            logger.info(f"Teleinfo listener started: {listener.running}")
