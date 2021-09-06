from django.conf import settings
from django.utils import timezone

from teleinformation.models import TeleinformationHistory
from django.core.management.base import BaseCommand

from housebrain_config.settings.constants import (
    SERIAL_PORT, SERIAL_BAUDRATE, SERIAL_TIMEOUT
)
from teleinformation.models import TeleinfoManager
teleinfo_manager = TeleinfoManager()

class Command(BaseCommand):
    help = """
    will save in database Teleinformation
    """
    def add_arguments(self, teleinfo_history_save):
        pass

    def handle(self, *args, **options):
        """main controler."""

        # get dictionary of all the fields in TeleinformationHistory model
        self.teleinfo = self.get_TeleinformationHistory_model_fields()

        if settings.UNPLUGGED_MODE:
            self.teleinfo = self.get_false_data_for_unplugged_mode()
            self.stdout.write("reading teleinfo in ---- UNPLUGGED_MODE ----")
        else :
            first_key_that_was_read  = ""
            teleinfo_is_complete = False
            serial_port = self.get_serial_port()
            # if there is data in serial port
            if serial_port.readline():
                # as long as the teleinfo has not completed a complete loop
                while not teleinfo_is_complete:
                    # for each line of the teleinfo frame
                    line = str(serial_port.readline())
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
        teleinfo_manager.save_teleinfo(self.teleinfo)


    def get_false_data_for_unplugged_mode(self):
        """ false data for the debug mode (no teleinfo connected) """
        false_teleinfo  = {}
        for key in self.teleinfo.keys():
            false_teleinfo[key] = "1"
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
        data = {}
        for key in self.teleinfo.keys():
            if key in line:
                data["key"] = key
                #get value in line
                data["value"] = line.split()[1]
                #get checsum in line
                #|can't use split because checksum can be a blanck char
                data["wanted_checksum"] = line[-6:][0]
                #and if the line is the last of the frame another way...
                if key == "MOTDETAT":
                    data["wanted_checksum"] = line[-14:][0]
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
