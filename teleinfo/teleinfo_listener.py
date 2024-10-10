import os
import serial
import threading


class TeleinfoListener:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate)
        self.running = True

    def listen(self):
        while self.running:
            if self.ser.in_waiting:
                data = self.ser.readline().decode("utf-8").strip()
                self.process_data(data)

    def process_data(self, data):
        # Logique pour traiter les données reçues
        print(f"Received: {data}")

    def stop(self):
        self.running = False
        self.ser.close()


def start_listener():
    unplugged_mode = os.getenv("UNPLUGGED_MODE", "False") == "True"

    if unplugged_mode:
        print("Running in unplugged mode. Teleinfo listener will not start.")
        print("(see .env to change mode)")
        return None  # Ne pas démarrer l'écouteur
    else:
        listener = TeleinfoListener("/dev/ttyUSB0", 1200)
        listener_thread = threading.Thread(target=listener.listen)
        listener_thread.daemon = (
            True  # Permet au thread de s'arrêter avec le programme principal
        )
        listener_thread.start()
        return listener
