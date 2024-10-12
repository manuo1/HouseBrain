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
from teleinfo.services import (
    add_data_to_buffer,
    get_data_in_line,
    teleinfo_frame_is_complete,
)


class TeleinfoListener:
    def __init__(self):
        self.ser = self.get_serial_port()
        self.running = True
        self.buffer = {}

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
        key, value = get_data_in_line(data)
        self.buffer = add_data_to_buffer(key, value, self.buffer)
        if teleinfo_frame_is_complete(self.buffer):
            print(self.buffer)
            self.buffer.clear()

    def stop(self):
        self.running = False
        self.ser.close()


def start_listener():

    if UNPLUGGED_MODE:
        print("Running in unplugged mode. Teleinfo listener will not start.")
        print("(see .env to change mode)")
        return None

    listener = TeleinfoListener()
    listener_thread = threading.Thread(target=listener.listen)
    listener_thread.daemon = True
    listener_thread.start()
    return listener
