import serial
import threading

from teleinfo.constants import (
    SERIAL_BYTESIZE,
    SERIAL_PARITY,
    SERIAL_PORT,
    SERIAL_BAUDRATE,
    SERIAL_STOPBITS,
    SERIAL_TIMEOUT,
    UNPLUGGED_MODE,
)
from teleinfo.services import get_data_in_line


class TeleinfoListener:
    def __init__(self):
        self.ser = self.get_serial_port()
        self.running = True

    def get_serial_port(self):
        serial_port = serial.Serial(
            port=SERIAL_PORT,
            baudrate=SERIAL_BAUDRATE,
            parity=SERIAL_PARITY,
            stopbits=SERIAL_STOPBITS,
            bytesize=SERIAL_BYTESIZE,
            timeout=SERIAL_TIMEOUT,
        )
        return serial_port

    def listen(self):
        while self.running:
            if self.ser.in_waiting:
                data = self.ser.readline()
                self.process_data(data)

    def process_data(self, data):
        # Logique pour traiter les données reçues
        a = []
        line_data = get_data_in_line(data)
        a.append(line_data)
        if len(a) > 5:
            print(a)
            a = []

    def stop(self):
        self.running = False
        self.ser.close()


def start_listener():

    if UNPLUGGED_MODE:
        print("Running in unplugged mode. Teleinfo listener will not start.")
        print("(see .env to change mode)")
        return None

    # Démarrer l'écouteur
    listener = TeleinfoListener()
    listener_thread = threading.Thread(target=listener.listen)
    listener_thread.daemon = (
        True  # Permet d'arrêter le thread avec le processus principal
    )
    listener_thread.start()
    return listener
