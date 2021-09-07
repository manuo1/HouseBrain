import time
from django.conf import settings
from django.utils import timezone

from teleinformation.models import TeleinfoManager
from django.core.management.base import BaseCommand

from housebrain_config.settings.constants import (
    SERIAL_PORT, SERIAL_BAUDRATE, SERIAL_TIMEOUT,
    ERROR_IINST, DEBUG_IINST, TELEINFO_TIMEOUT,
)

teleinfo_manager = TeleinfoManager()

class Command(BaseCommand):
    help = """
    will read and save IINST in teleinformation frame for power monitoring
    """
    def add_arguments(self, update_power_monitoring):
        pass

    def handle(self, *args, **options):
        """main controler."""

        self.iinst = ERROR_IINST

        if settings.UNPLUGGED_MODE:
            self.iinst = DEBUG_IINST
            self.stdout.write("reading teleinfo IINST in ---- UNPLUGGED_MODE ----")
        else :
            timeout = TELEINFO_TIMEOUT
            timeout_start = time.time()
            serial_port = self.get_serial_port()
            # as long as the iinst value is not read or the timeout is exceeded
            while self.iinst == ERROR_IINST or time.time() < (timeout_start + timeout):
                if serial_port.readline():
                    # read a line
                    line = str(serial_port.readline())
                    # extract data if "IINST" is present in line
                    if "IINST" in line:
                        data = self.get_data_in_line(line)
                        # checks if the data is valid with the checksum
                        if self.data_is_valid(data):
                            # and finaly store data in teleinfo dict
                            self.iinst = int(data["value"])
        self.stdout.write("IINST = " + str(self.iinst))
        teleinfo_manager.save_power_monitoring(self.iinst)


    def get_data_in_line(self, line):
        # check if a teleinfo key is present in the line
        data = {}
        data["key"] = "IINST"
        #get value in line
        data["value"] = line.split()[1]
        #get checsum in line
        #|can't use split because checksum can be a blanck char
        data["wanted_checksum"] = line[-6:][0]
        return data



    def data_is_valid(self, data):
        """
        The "checksum" is calculated on the whole of the characters
        going from the beginning of the label field to the end of
        the given field, spacing character (SP) included.
        First of all, the ASCII codes of all these characters are
        summed. To avoid introducing ASCII functions (00 to 31),
        we keep only the six least significant bits of the result
        obtained (this operation results in a logical AND between
        the sum previously calculated and 63). Finally, we add 32.
        The result will always be a printable ASCII character
        (sign, number, capital letter) going from 32 to 95.
        """

        #add spacing character ASCII codes
        calculated_checksum = 32
        #adds the sum of the ascii codes of the label characters
        calculated_checksum += sum([ord(char) for char in data["key"]])
        #adds the sum of the ascii codes of the data characters
        calculated_checksum += sum([ord(char) for char in data["value"]])
        #logical AND between the sum previously calculated and 63
        calculated_checksum = calculated_checksum & 63
        #Finally, we add 32
        calculated_checksum = chr(calculated_checksum + 32)

        return calculated_checksum == data["wanted_checksum"]

    def get_serial_port(self):
        """ Raspberry serial port config """
        import serial
        serial_port = serial.Serial(
            port=SERIAL_PORT,
            baudrate = SERIAL_BAUDRATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS,
            timeout=SERIAL_TIMEOUT
        )
        return serial_port
