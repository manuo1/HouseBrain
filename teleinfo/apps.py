import logging
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from result import Err, Ok


logger = logging.getLogger("django")


def start_listener_after_migrations(sender, **kwargs):
    from teleinfo.teleinfo_listener import start_listener

    logger.info("[TeleinfoListener] Initializing...")
    match start_listener():
        case Ok(_):
            logger.info("[TeleinfoListener] Started")
        case Err(e):
            logger.error(e)


class TeleinfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teleinfo"

    def ready(self):
        post_migrate.connect(start_listener_after_migrations, sender=self)
