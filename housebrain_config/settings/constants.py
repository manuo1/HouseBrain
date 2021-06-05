
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
# Maximum consecutive reading errors before defining the sensor defective
MAX_SENSOR_READING_ERRORS = 10

##############################################################################
# Raspberry one wire devices folder paths:
##############################################################################
W1_DIRECTORY_PATH = "/sys/bus/w1/devices"
TEMPERATURE_FILE = "/temperature"
