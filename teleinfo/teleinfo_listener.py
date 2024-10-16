from datetime import datetime
import logging
import serial
import threading
from result import Err, Ok
from teleinfo.constants import SerialConfig, UNPLUGGED_MODE, Teleinfo
from django.utils import timezone
from teleinfo.mutators import save_teleinfo
from teleinfo.selectors import get_last_teleinfo_created_datetime
from teleinfo.services import (
    buffer_can_accept_new_data,
    get_data_in_line,
    teleinfo_frame_is_complete,
)

logger = logging.getLogger(__name__)


class TeleinfoListener:
    def __init__(self) -> None:
        self.serial_port = self.get_serial_port()
        self.running = True
        self.buffer = {}
        self.teleinfo = Teleinfo()
        self.lock = threading.Lock()  # Verrou pour empêcher un accès concurrent

        # récupère le last_save en bdd
        match get_last_teleinfo_created_datetime():
            case Ok(last_teleinfo_dt):
                self.teleinfo.last_save = last_teleinfo_dt
            case Err(_):
                self.teleinfo.last_save = datetime.min.replace(
                    tzinfo=timezone.get_current_timezone()
                )

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
            logger.error(f"[TeleinfoListener] Error opening serial port: {e}")
            raise  # Relancer l'exception à traiter plus haut

    def listen(self) -> None:
        while self.running:
            print("while self.running")
            try:
                if self.serial_port.in_waiting:
                    print("self.serial_port.in_waiting")
                    raw_data_line = self.serial_port.readline()
                    print(raw_data_line)
                    self.process_data(raw_data_line)
            except serial.SerialException as e:
                logger.error(f"[TeleinfoListener] Error reading from serial port: {e}")
                break
            except Exception as e:
                logger.error(f"[TeleinfoListener] Unexpected error in listener: {e}")

    def perform_functions_using_teleinfo(self):
        match save_teleinfo(self.teleinfo):
            case Ok(saved):
                if saved:
                    self.teleinfo.last_save = self.teleinfo.created
                else:
                    pass
            case Err(e):
                logger.error(e)
                return
        # save indexes
        # monitor overconsumption and shed load
        return

    def process_data(self, raw_data_line: bytes) -> None:
        match get_data_in_line(raw_data_line):
            case Ok(data):
                key, value = data
            case Err(e):
                logger.error(f"[TeleinfoListener] {e}")
                return
        match buffer_can_accept_new_data(key, self.buffer):
            case Ok(buffer_can_accept):
                if buffer_can_accept:
                    self.buffer[key] = value
                else:
                    return
            case Err(e):
                logger.error(f"[TeleinfoListener] {e}")
                return
        match teleinfo_frame_is_complete(self.buffer):
            case Ok(is_complete):
                if is_complete:
                    self.teleinfo.created = timezone.now()
                    self.teleinfo.data = self.buffer.copy()
                    self.buffer.clear()
                    print("teleinfo complete")
                    print(self.teleinfo)
                    self.perform_functions_using_teleinfo()
                else:
                    print("teleinfo incomplete")
                    print(self.buffer)

                    return
            case Err(e):
                logger.error(f"[TeleinfoListener] {e}")
                return

    def stop(self) -> None:
        self.running = False
        try:
            self.serial_port.close()
        except serial.SerialException as e:
            logger.error(f"[TeleinfoListener] Error closing serial port: {e}")
        logger.info("[TeleinfoListener] stopped.")


def start_listener() -> TeleinfoListener:
    if UNPLUGGED_MODE:
        logger.warning(
            "[TeleinfoListener] Running in unplugged mode. Teleinfo listener will not start.\n"
        )
        return None

    listener = TeleinfoListener()
    listener_thread = threading.Thread(target=listener.listen)
    listener_thread.daemon = True
    listener_thread.start()
    print("[TeleinfoListener] Teleinfo listener thread started.")
    logger.info("[TeleinfoListener] Teleinfo listener thread started.")
    return listener

    # TODO verifier si le .lock ne dois pas être mis sur le listener_thread et aps le listener
