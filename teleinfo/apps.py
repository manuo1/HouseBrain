import logging
from django.apps import AppConfig


logger = logging.getLogger(__name__)


class TeleinfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teleinfo"

    def ready(self):
        logger.info("Initializing Teleinfo listener...")
        from teleinfo.teleinfo_listener import start_listener

        listener = start_listener()

        if listener:
            logger.info(f"Teleinfo listener started: {listener.running}")
        else:
            logger.warning(
                "Teleinfo listener could not be started. Running in unplugged mode."
            )
