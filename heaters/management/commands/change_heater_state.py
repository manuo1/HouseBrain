from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """
    will manage the real state of heaters
    """
    def add_arguments(self, change_heater_state):

        change_heater_state.add_argument(
            'pin',
            type=int,
            help='Define MCP23017 pin used',
        )
        change_heater_state.add_argument(
            'state',
            type=str,
            help='State of the pin (ON or OFF) ',
        )


    def handle(self, *args, **options):
        """main controler."""

        if settings.UNPLUGGED_MODE:
            self.stdout.write(
                "change heater mode" + " " +
                str(options['pin']) + " " +
                options['state']
            )

        else:
            # import Raspberry modules for I2C and MCP23017

            # MCP23017 is a port expander that gives you virtually identical
            #| PORTS compared to standard microcontrollers e.g. Arduino or PIC
            #| devices and it even includes interrupts. It gives you an
            #| extra 16 I/O pins using an I2C interface as well as
            #| comprehensive interrupt control

            import board
            import busio
            from adafruit_mcp230xx.mcp23017 import MCP23017
            # Initialize the I2C bus:
            i2c = busio.I2C(board.SCL, board.SDA)

            # Create an instance of MCP23017 class
            mcp = MCP23017(i2c)

            # Now call the get_pin function to get an instance of a pin on
            #| the chip. This instance will act just like a
            #| digitalio.DigitalInOut class instance and has all the same
            #| properties and methods (except you can't set pull-down
            #| resistors, only pull-up!).  For the MCP23017 you specify a pin
            #| number from 0 to 15

            mcp_pin = mcp.get_pin(options['pin'])
            # Setup pin as an output that's at a high logic level.
            mcp_pin.switch_to_output(value=True)


            # apply the new pin state
            if options['state'] == "ON":
                mcp_pin.value = True
            elif options['state'] == "OFF":
                mcp_pin.value = False
            else:
                mcp_pin.value = False
