import logging
from django.apps import AppConfig
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)


def start_listener_after_migrations(sender, **kwargs):
    from teleinfo.teleinfo_listener import start_listener

    logger.info("[TeleinfoListener] Initializing...")
    print("[TeleinfoListener] Initializing...")
    listener = start_listener()

    if listener:
        logger.info(f"[TeleinfoListener] started: {listener.running}")
        print(f"[TeleinfoListener] started: {listener.running}")
    else:
        logger.warning(
            "[TeleinfoListener] could not be started. Running in unplugged mode."
        )


class TeleinfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teleinfo"

    def ready(self):
        post_migrate.connect(start_listener_after_migrations, sender=self)
