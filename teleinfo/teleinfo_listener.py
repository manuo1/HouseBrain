import logging
import serial
import threading
from result import Err, Ok
from teleinfo.constants import (
    SerialConfig,
    UNPLUGGED_MODE,
)
from teleinfo.services import (
    buffer_can_accept_new_data,
    get_data_in_line,
    teleinfo_frame_is_complete,
)

logger = logging.getLogger(__name__)


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
        match get_data_in_line(raw_data_line):
            case Ok(data):
                key, value = data
            case Err(e):
                logger.error(e)
                return
        match buffer_can_accept_new_data(key, self.buffer):
            case Ok(_):
                self.buffer[key] = value
            case Err(e):
                logger.info(e)
                return

        match teleinfo_frame_is_complete(self.buffer):
            case Ok(_):
                print(self.buffer)
                # do something
                self.buffer.clear()
            case Err(e):
                return

    def stop(self) -> None:
        self.running = False
        self.ser.close()


def start_listener() -> TeleinfoListener:

    if UNPLUGGED_MODE:
        logger.info("Running in unplugged mode. Teleinfo listener will not start.\n")
        return None

    listener = TeleinfoListener()
    listener_thread = threading.Thread(target=listener.listen)
    listener_thread.daemon = True
    listener_thread.start()
    return listener
