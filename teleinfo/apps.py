from django.apps import AppConfig
from django.db.models.signals import post_migrate
from teleinfo.tasks import test_task


class TeleinfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teleinfo"

    def ready(self):
        post_migrate.connect(self.launch_celery_task)

    def launch_celery_task(self, sender, **kwargs):
        test_task.delay()
