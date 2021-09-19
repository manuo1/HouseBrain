import time
from django.conf import settings
from django.utils import timezone

from teleinformation.models import TeleinfoManager
from django.core.management.base import BaseCommand

from housebrain_config.settings.constants import (
    SERIAL_PORT, SERIAL_BAUDRATE, SERIAL_TIMEOUT,
    ERROR_IINST, DEBUG_IINST, ERROR_ISOUSC, DEBUG_ISOUSC,
    REMAINING_POWER_MONITORING_STEPS, CRITICAL_REMAINING_POWER,
    TELEINFO_TIMEOUT,
)

teleinfo_manager = TeleinfoManager()

class Command(BaseCommand):
    help = """
    will check IINST in teleinformation frame for power monitoring
    """
    def add_arguments(self, power_monitoring):
        pass

    def handle(self, *args, **options):
        """main controler."""

        self.monitoring = {"IINST": ERROR_IINST, "ISOUSC": ERROR_ISOUSC}

        if settings.UNPLUGGED_MODE:
            self.monitoring["IINST"] = DEBUG_IINST
            self.monitoring["ISOUSC"] = DEBUG_ISOUSC

            self.stdout.write(
                "reading teleinfo IINST in ---- UNPLUGGED_MODE ----"
            )
        else :
            timeout_start = time.time()
            serial_port = self.get_serial_port()
            # if there is data in serial port
            if serial_port.readline():
                # as long as self.monitoring is not complet
                while not self.monitoring_is_complete():
                    # break if timout
                    if time.time() > (timeout_start + TELEINFO_TIMEOUT):
                        break
                    # for each line of the teleinfo frame
                    line = str(serial_port.readline())
                    # get data in the line
                    data_in_ligne = self.get_data_in_line(line)
                    # checks if the data is valid
                    if self.data_is_valid(data_in_ligne):
                        # if valid => store data
                        self.monitoring[data_in_ligne["key"]] = int(data_in_ligne["value"])
        # add the remaining prower to the monitoring
        self.monitoring["percentage_remaining_power"] = self.percentage_remaining_power()
        # update power monitoring only if the remaining power has changed steps
        if self.percentage_remaining_power_has_changed():
            teleinfo_manager.update_power_monitoring(self.monitoring)
            # save new entry if remaining power is critical
            if self.remaining_power_is_critical():
                teleinfo_manager.save_critical_remaining_power(self.monitoring)


    def remaining_power_is_critical(self):
        return self.monitoring["percentage_remaining_power"] < CRITICAL_REMAINING_POWER

    def percentage_remaining_power_has_changed(self):
        last_power_remaining = teleinfo_manager.get_last_power_monitoring().percentage_remaining_power
        new_power_remaining = self.monitoring["percentage_remaining_power"]
        return last_power_remaining != new_power_remaining


    def percentage_remaining_power(self):
        # real percentage of remaining power
        real_percentage = 100-(self.monitoring["IINST"] / self.monitoring["ISOUSC"]*100)
        percentage_remaining_power = 0
        for step in sorted(REMAINING_POWER_MONITORING_STEPS):
            if real_percentage > step:
                percentage_remaining_power = step
        return percentage_remaining_power

    def monitoring_is_complete(self):
        check = self.monitoring["IINST"] != ERROR_IINST and self.monitoring["ISOUSC"] != ERROR_ISOUSC
        return check


    def get_data_in_line(self, line):
        # check if a teleinfo key is present in the line
        data_in_ligne = {}
        for key in self.monitoring.keys():
            if key in line:
                data_in_ligne["key"] = key
                #get value in line
                data_in_ligne["value"] = line.split()[1]
                #get checsum in line
                #|can't use split because checksum can be a blanck char
                data_in_ligne["wanted_checksum"] = line[-6:][0]
                #and if the line is the last of the frame another way...
                if key == "MOTDETAT":
                    data_in_ligne["wanted_checksum"] = line[-14:][0]
        return data_in_ligne



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
        data_is_valid = False
        if len(data) == 3 :
            #add spacing character ASCII codes
            calculated_checksum = 32
            #adds the sum of the ascii codes of the label characters
            #| ord() return an integer representing the Unicode code point
            #| of that character
            calculated_checksum += sum([ord(char) for char in data["key"]])
            #adds the sum of the ascii codes of the data characters
            calculated_checksum += sum([ord(char) for char in data["value"]])
            #logical AND between the sum previously calculated and 63
            calculated_checksum = calculated_checksum & 63
            #Finally, we add 32
            calculated_checksum = chr(calculated_checksum + 32)
            # check if calculated = wanted
            data_is_valid = calculated_checksum == data["wanted_checksum"]

        return data_is_valid

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
