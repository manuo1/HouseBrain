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
        self.lock = threading.Lock()  # Ajout d'un verrou pour gérer l'accès concurrent

    def get_serial_port(self) -> serial.Serial:
        try:
            serial_port = serial.Serial(
                port=SerialConfig.PORT.value,
                baudrate=SerialConfig.BAUDRATE.value,
                parity=SerialConfig.PARITY.value,
                stopbits=SerialConfig.STOPBITS.value,
                bytesize=SerialConfig.BYTESIZE.value,
                timeout=SerialConfig.TIMEOUT.value,
            )
            return serial_port
        except serial.SerialException as e:
            logger.error(f"Error opening serial port: {e}")
            raise  # Re-raise the exception to be handled higher up

    def listen(self) -> None:
        while self.running:
            try:
                if self.ser.in_waiting:
                    raw_data_line = self.ser.readline()
                    self.process_data(raw_data_line)
            except serial.SerialException as e:
                logger.error(f"Error reading from serial port: {e}")
                break  # Exit the loop if there's an issue with the serial connection
            except Exception as e:
                logger.error(f"Unexpected error in listener: {e}")

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
        try:
            self.ser.close()
        except serial.SerialException as e:
            logger.error(f"Error closing serial port: {e}")
        logger.info("Teleinfo listener stopped.")


def start_listener() -> TeleinfoListener:
    if UNPLUGGED_MODE:
        logger.info("Running in unplugged mode. Teleinfo listener will not start.\n")
        return None

    listener = TeleinfoListener()
    listener_thread = threading.Thread(target=listener.listen)
    listener_thread.daemon = (
        True  # Ensures the thread terminates when the main program exits
    )
    listener_thread.start()
    logger.info("Teleinfo listener thread started.")
    return listener
