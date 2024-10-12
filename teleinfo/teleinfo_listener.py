import serial
import threading

from teleinfo.constants import (
    SerialConfig,
    UNPLUGGED_MODE,
)
from teleinfo.services import (
    buffer_can_accept_new_data,
    get_data_in_line,
    teleinfo_frame_is_complete,
)


class TeleinfoListener:
    def __init__(self) -> None:
        self.ser = self.get_serial_port()
        self.running = True
        self.buffer = {}

    def get_serial_port(self) -> serial.Serial:
        serial_port = serial.Serial(
            port=SerialConfig.PORT.value,
            baudrate=SerialConfig.BAUDRATE.value,
            parity=SerialConfig.PARITY.value,
            stopbits=SerialConfig.STOPBITS.value,
            bytesize=SerialConfig.BYTESIZE.value,
            timeout=SerialConfig.TIMEOUT.value,
        )
        return serial_port

    def listen(self) -> None:
        while self.running:
            if self.ser.in_waiting:
                raw_data_line = self.ser.readline()
                self.process_data(raw_data_line)

    def process_data(self, raw_data_line: bytes) -> None:
        key, value = get_data_in_line(raw_data_line)
        if buffer_can_accept_new_data(key, self.buffer):
            self.buffer[key] = value
        if teleinfo_frame_is_complete(self.buffer):
            print(self.buffer)
            self.buffer.clear()

    def stop(self) -> None:
        self.running = False
        self.ser.close()


def start_listener() -> TeleinfoListener:

    if UNPLUGGED_MODE:
        print("Running in unplugged mode. Teleinfo listener will not start.")
        print("(see .env to change mode)")
        return None

    listener = TeleinfoListener()
    listener_thread = threading.Thread(target=listener.listen)
    listener_thread.daemon = True
    listener_thread.start()
    return listener
