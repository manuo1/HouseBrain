from datetime import datetime
import logging
import serial

from core.constants import UNPLUGGED_MODE
from load_shedding.sevices import manage_load_shedding
from result import Err, Ok, Result
from teleinfo.constants import SerialConfig, Teleinfo
from django.utils import timezone
from teleinfo.mutators import save_teleinfo
from teleinfo.services import (
    add_available_power_to_cache,
    buffer_can_accept_new_data,
    get_data_in_line,
    teleinfo_frame_is_complete,
)

logger = logging.getLogger("django")


class TeleinfoListener:
    def __init__(self) -> None:
        self.running = True
        self.buffer = {}
        self.teleinfo = Teleinfo()
        self.serial_port = serial.Serial(
            port=SerialConfig.PORT.value,
            baudrate=SerialConfig.BAUDRATE.value,
            parity=SerialConfig.PARITY.value,
            stopbits=SerialConfig.STOPBITS.value,
            bytesize=SerialConfig.BYTESIZE.value,
            timeout=SerialConfig.TIMEOUT.value,
        )
        self.teleinfo.last_save = datetime.min.replace(
            tzinfo=timezone.get_current_timezone()
        )

    def listen(self) -> None:
        logger.info("[TeleinfoListener] Listening on serial port...")
        while self.running:
            try:
                # si des données sont disponibles dans le buffer du port série
                if self.serial_port.in_waiting:
                    raw_data_line = self.serial_port.readline()
                    self.process_data(raw_data_line)
            except serial.SerialException as e:
                logger.error(f"[TeleinfoListener] Error reading from serial port: {e}")
                break

    def perform_functions_using_teleinfo(self) -> None:
        # coupe tous les chauffage si on est en dépassement d'intensité
        manage_load_shedding(self.teleinfo)

        # stock la puissance disponible dans le cache
        match add_available_power_to_cache(self.teleinfo):
            case Ok(_):
                pass
            case Err(e):
                logger.error(f"[TeleinfoListener] {e}")

        # sauvegarde la teleinfo toutes les heures
        match save_teleinfo(self.teleinfo):
            case Ok(saved):
                if saved:
                    self.teleinfo.last_save = self.teleinfo.created
                    logger.info(f"[TeleinfoListener] Saved : {self.teleinfo}")
                else:
                    pass
            case Err(e):
                logger.error(f"[TeleinfoListener] {e}")

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
            case Ok(frame_is_complete):
                if frame_is_complete:
                    self.teleinfo.created = timezone.now()
                    self.teleinfo.data = self.buffer.copy()
                    self.buffer.clear()
                    self.perform_functions_using_teleinfo()
                else:
                    return
            case Err(e):
                logger.error(f"[TeleinfoListener] {e}")
                return

    def stop(self) -> None:
        self.running = False
        try:
            self.serial_port.close()
            logger.info("[TeleinfoListener] stopped.")
        except serial.SerialException as e:
            logger.error(f"[TeleinfoListener] Error closing serial port: {e}")


def start_listener() -> Result[TeleinfoListener, str]:
    if UNPLUGGED_MODE:
        return Err(
            "[TeleinfoListener] Running in unplugged mode. Teleinfo listener will not start.\n"
        )
    listener = TeleinfoListener()
    return Ok(listener)
