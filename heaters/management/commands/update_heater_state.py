from django.conf import settings
from django.core.management.base import BaseCommand
from heaters.models import HeaterManager
from housebrain_config.settings.constants import (
    HEATERS_PILOTING_MODE as piloting_mode
)

heater_manager = HeaterManager()

class Command(BaseCommand):
    help = """
    will manage the real state of heaters
    """
    def add_arguments(self, update_heater_state):
        pass

    def handle(self, *args, **options):
        """main controler."""

        pin_states = self.all_heaters_states()


        if settings.UNPLUGGED_MODE:
            self.stdout.write("heater states in ---- UNPLUGGED_MODE ----")
            for pin, state in pin_states:
                self.stdout.write(str(pin) + " , " + str(state))

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

            for pin, state in pin_states:
                mcp_pin = mcp.get_pin(pin)
                # Setup pin as an output that's at a high logic level.
                if piloting_mode == "on when off":
                    mcp_pin.switch_to_output(value= not state)
                else:
                    mcp_pin.switch_to_output(value=state)


    def all_heaters_states(self):
        pin_states = []
        for heater in heater_manager.all_heaters():
            pin_states.append((heater.control_pin, heater.is_on))
        return pin_states
