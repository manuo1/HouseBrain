from django.apps import AppConfig
from teleinfo.teleinfo_listener import start_listener


class TeleinfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teleinfo"

    def ready(self):
        print("Starting Teleinfo listener")
        listener = start_listener()
        if listener:
            print(f"Teleinfo listener started: {listener.running}")
