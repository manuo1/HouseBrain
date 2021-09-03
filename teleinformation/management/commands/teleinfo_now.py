from django.conf import settings
from django.utils import timezone

from teleinformation.models import TeleinformationHistory
from django.core.management.base import BaseCommand

from housebrain_config.settings.constants import (
    SERIAL_PORT, SERIAL_BAUDRATE, SERIAL_TIMEOUT
)

class Command(BaseCommand):
    help = """
    will save in database Teleinformation
    """
    def add_arguments(self, teleinfo_now):
        pass

    def handle(self, *args, **options):
        """main controler."""

        """ create dictionary of all the fields in TeleinformationHistory model """

        # Get an instance of TeleinformationHistory model
        instance = TeleinformationHistory()
        # list all attributes and remove 2 first
        # (2 first are _state and id )
        model_fields_list = list(instance.__dict__.keys())[2:]
        # Create the dictionary with blank values
        teleinfo = {key: "" for key in model_fields_list}



        """ false data for the debug mode (no teleinfo connected) """
        if settings.UNPLUGGED_MODE:
            for key in teleinfo.keys():
                teleinfo[key] = "1"
            self.stdout.write("---- UNPLUGGED_MODE ----")
        else :
            first_key_that_was_read  = ""
            teleinfo_is_complete = False
            
            import serial
            serial_port = serial.Serial(
                port=SERIAL_PORT,
                baudrate = SERIAL_BAUDRATE,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.SEVENBITS,
                timeout=SERIAL_TIMEOUT
            )
            # if there is data in serial port
            if serial_port.readline():
                # as long as the teleinfo has not completed a complete loop
                while not teleinfo_is_complete:
                    # for each line of the teleinfo frame
                    line = str(serial_port.readline())
                    data = get_data_in_line(line)
                    # if the key corresponds to the one read first, the
                    # | teleinfo has made a complete loop
                    if data[key] == first_key_that_was_read:
                        teleinfo_is_complete = True
                        break
                    # checks if the data is valid with the checksum
                    if data_is_valid(data):
                        # and finaly store data in teleinfo dict
                        if all(value == "" for value in teleinfo.values()):
                            first_key_that_was_read  = data[key]
                            teleinfo[data[key]] = data[value]
        for key, value in teleinfo.items():
            self.stdout.write(key + " = " + value)


    def get_data_in_line(line):
        # check if a teleinfo key is present in the line
        data = {}
        for key in teleinfo.keys():
            if key in line:
                data["key"] = key
                #get value in line
                data["value"] = line.split()[1]
                #get checsum in line
                data["wanted_checksum"] = line.split()[2][0:1]
        return data



    def data_is_valid(key, value, wanted_checksum):
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
        calculated_checksum += sum([ord(char) for char in key])
        #adds the sum of the ascii codes of the data characters
        calculated_checksum += sum([ord(char) for char in value])
        #logical AND between the sum previously calculated and 63
        calculated_checksum = calculated_checksum & 63
        #Finally, we add 32
        calculated_checksum = chr(calculated_checksum + 32)

        return calculated_checksum == wanted_checksum
