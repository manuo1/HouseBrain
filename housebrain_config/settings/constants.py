
##############################################################################
#false data for the debug mode (no sensor connected):
##############################################################################
DEBUG_SENSOR_FOLDER_PATHS = [
    '/sys/bus/w1/devices/28-000005c7cc82',
    '/sys/bus/w1/devices/28-000005c83f61',
    '/sys/bus/w1/devices/28-000005c7d98e',
    '/sys/bus/w1/devices/28-000005c6f49f',
    '/sys/bus/w1/devices/28-000005c83686',
    '/sys/bus/w1/devices/28-000005c6d2aa',
    '/sys/bus/w1/devices/28-000005c7824f',
    '/sys/bus/w1/devices/28-000005c6d680'
]
DEBUG_TEMPERATURE = 54321

##############################################################################
# Temperature sensors settings :
##############################################################################
ERROR_TEMPERATURE = 85000
MAX_TEMPERATURE = 60000
MIN_TEMPERATURE = -50000
MAX_DELTA_TEMPERATURE = 4
# Maximum consecutive reading errors before defining the sensor defective
MAX_SENSOR_READING_ERRORS = 10
TEMPERATURE_HISTORY_DELTA = 30 # save temperature history every X minutes

##############################################################################
# Raspberry one wire devices folder paths:
##############################################################################
W1_DIRECTORY_PATH = "/sys/bus/w1/devices"
TEMPERATURE_FILE = "/temperature"

##############################################################################
# Raspberry serial port reading settings (teleinfo):
##############################################################################
SERIAL_PORT='/dev/ttyS0'
SERIAL_BAUDRATE = 1200
SERIAL_TIMEOUT=1

##############################################################################
# Teleinformation
##############################################################################
ERROR_IINST = 999
DEBUG_IINST = 999
ERROR_ISOUSC = 1
DEBUG_ISOUSC = 1
TELEINFO_TIMEOUT = 10 # [seconds]
TELEINFO_HISTORY_DELTA = 30 # save teleinformation history every X minutes

##############################################################################
# Heating manager
##############################################################################
MANAGE_HEATERS_TIMEOUT = 10 # [seconds]
HEATER_VOLTAGE = 220

##############################################################################
# HEATERS PILOTING MODE
##############################################################################


#the heating is controlled by pilot wire, when you want to stop the heating,
#| a signal is sent to the radiator (negative half-wave) to place the heating in
#| frost protection position. You must therefore activate the output to turn off
#| the heating.


#The "HEATERS_PILOTING_MODE" value:
#| in position "on when on": turns on the heating when the output is activated
#| in position "on when off": turns on the heating when the output is deactivated

HEATERS_PILOTING_MODE = "on when off"
