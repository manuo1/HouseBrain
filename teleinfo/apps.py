import logging
from django.apps import AppConfig
from result import Err, Ok


logger = logging.getLogger("django")


class TeleinfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teleinfo"

    def ready(self):
        # start listener after migrations
        # post_migrate.connect(start_listener_after_migrations, sender=self)
        from teleinfo.teleinfo_listener import start_listener

        logger.info("[TeleinfoListener] Initializing...")
        match start_listener():
            case Ok(listener):
                logger.info(
                    f"[TeleinfoListener] Teleinfo listener is active. {listener.created}"
                )
            case Err(e):
                logger.error(e)
