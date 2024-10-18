from django.apps import AppConfig


class TeleinfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teleinfo"

    # def ready(self):
    #     post_migrate.connect(self.launch_celery_task)

    # def launch_celery_task(self, sender, **kwargs):
    #     test_task.delay()
