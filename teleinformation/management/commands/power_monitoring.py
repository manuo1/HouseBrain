import serial
import time
from django.conf import settings
from django.utils import timezone
from django.core import management
from django.core.management.base import BaseCommand

from housebrain_config.settings.constants import (
    SERIAL_PORT, SERIAL_BAUDRATE, SERIAL_TIMEOUT,
    ERROR_IINST, DEBUG_IINST, ERROR_ISOUSC, DEBUG_ISOUSC,
    TELEINFO_TIMEOUT, TELEINFO_HISTORY_DELTA,
)
from teleinformation.models import TeleinformationHistory
from teleinformation.models import TeleinfoManager
from heaters.models import HeaterManager

teleinfo_manager = TeleinfoManager()
heater_manager = HeaterManager()

class Command(BaseCommand):
    help = """
    will save in database Teleinformation
    """
    def add_arguments(self, power_monitoring):
        pass

    def handle(self, *args, **options):
        """main controler."""

        # get dictionary of all the fields in TeleinformationHistory model
        self.teleinfo = self.get_TeleinformationHistory_model_fields()
        self.monitoring = {"IINST": ERROR_IINST, "ISOUSC": ERROR_ISOUSC}

        if settings.UNPLUGGED_MODE:
            self.teleinfo = self.get_false_data_for_unplugged_mode()
            self.stdout.write("reading teleinfo in ---- UNPLUGGED_MODE ----")
        else :
            timeout_start = time.time()
            first_key_that_was_read  = ""
            teleinfo_is_complete = False
            serial_port = self.get_serial_port()
            # if there is data in serial port
            if serial_port.readline():
                # as long as the teleinfo has not completed a complete loop
                while not teleinfo_is_complete:
                    line = ""
                    # break if timout
                    if time.time() > (timeout_start + TELEINFO_TIMEOUT):
                        break
                    # for each line of the teleinfo frame
                    try:
                        line = str(serial_port.readline())
                    except serial.serialutil.SerialException as e:
                        self.stdout.write(f'# device returned no data\n-->{e}')
                    data = self.get_data_in_line(line)
                    # if the key corresponds to the one read first, the
                    # | teleinfo has made a complete loop
                    if data["key"] == first_key_that_was_read:
                        teleinfo_is_complete = True
                    # checks if the data is valid with the checksum
                    if self.data_is_valid(data) and not teleinfo_is_complete:
                        # store the first key read in frame
                        if all(value == "" for value in self.teleinfo.values()):
                            first_key_that_was_read  = data["key"]
                        # and finaly store data in teleinfo dict
                        self.teleinfo[data["key"]] = data["value"]
        self.teleinfo["date_time"] = timezone.now()
        # save teleinfo every *TELEINFO_HISTORY_DELTA* minutes
        if self.teleinfo["date_time"].minute % TELEINFO_HISTORY_DELTA == 0:
            teleinfo_manager.save_teleinfo(self.teleinfo)
        self.monitoring = self.build_monitoring_data()
        # update power monitoring
        teleinfo_manager.update_power_monitoring(self.monitoring)
        # save new entry if remaining power is critical
        if self.remaining_power_is_critical():
            teleinfo_manager.save_critical_remaining_power(self.monitoring)
            heater_manager.turn_off_all_heaters()
            management.call_command('manage_heaters')

    def remaining_power_is_critical(self):
        return self.monitoring["IINST"] >= self.monitoring["ISOUSC"]

    def build_monitoring_data(self):
        monitoring = {}
        monitoring["IINST"] = int(self.teleinfo["IINST"])
        monitoring["ISOUSC"] = int(self.teleinfo["ISOUSC"])
        return monitoring


    def get_false_data_for_unplugged_mode(self):
        """ false data for the debug mode (no teleinfo connected) """
        false_teleinfo  = {}
        for key in self.teleinfo.keys():
            false_teleinfo[key] = "1"
        false_teleinfo["IINST"] = DEBUG_IINST
        false_teleinfo["ISOUSC"] = DEBUG_ISOUSC
        return false_teleinfo


    def get_TeleinformationHistory_model_fields(self):
        """ create dictionary of all TeleinformationHistory attributes """
        teleinfo  = {}
        # Get an instance of TeleinformationHistory model
        instance = TeleinformationHistory()
        # list all attributes and remove 2 first
        # (we don't need the 2 first which are _state and id )
        model_fields_list = list(instance.__dict__.keys())[2:]
        # Create the dictionary with blank values
        teleinfo = {key: "" for key in model_fields_list}
        return teleinfo


    def get_data_in_line(self, line):
        # check if a teleinfo key is present in the line
        data = {"key" : "", "value" : "", "read_checksum" : ""}
        for key in self.teleinfo.keys():
            if key in line:
                data["key"] = key
                #get value in line
                data["value"] = line.split()[1]
                #get checksum in line
                #|can't use split because checksum can be a blanck char
                data["read_checksum"] = line[-6:][0]
                #and if the line is the last of the frame another way...
                if key == "MOTDETAT":
                    data["read_checksum"] = line[-14:][0]
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

        return calculated_checksum == data["read_checksum"]



    def get_serial_port(self):
        """ Raspberry serial port config """
        serial_port = serial.Serial(
            port=SERIAL_PORT,
            baudrate = SERIAL_BAUDRATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS,
            timeout=SERIAL_TIMEOUT
        )
        return serial_port
