import logging
from django.apps import AppConfig
from result import Err, Ok
from django.db.models.signals import post_migrate

logger = logging.getLogger("django")


def start_listener_after_migrations(sender, **kwargs):
    from teleinfo.teleinfo_listener import start_listener

    logger.info("[TeleinfoListener] Initializing...")
    match start_listener():
        case Ok(_):
            pass
        case Err(e):
            logger.error(e)


class TeleinfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teleinfo"

    def ready(self):
        post_migrate.connect(start_listener_after_migrations, sender=self)
