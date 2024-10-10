import threading
import os
from django.apps import AppConfig
from teleinfo.teleinfo_listener import TeleinfoListener


class TeleinfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teleinfo"

    def ready(self):
        unplugged_mode = os.getenv("UNPLUGGED_MODE", "False") == "True"

        if unplugged_mode:
            print("Running in unplugged mode. Teleinfo listener will not start.")
            print("(see .env to change mode)")
            return None  # Ne pas démarrer l'écouteur

        # Vérifiez que l'écouteur n'est pas déjà en cours d'exécution
        if not hasattr(self, "listener") or not self.listener.running:
            self.listener = TeleinfoListener("/dev/ttyUSB0", 1200)
            listener_thread = threading.Thread(target=self.listener.listen)
            # Permet au thread de s'arrêter avec le programme principal
            listener_thread.daemon = True
            listener_thread.start()
