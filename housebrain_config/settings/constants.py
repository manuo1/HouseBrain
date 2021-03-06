from django.conf import settings
from housebrain_config.settings.messages import (
    DAYOFTHEWEEK_MONDAY,
    DAYOFTHEWEEK_TUESDAY,
    DAYOFTHEWEEK_WEDNESDAY,
    DAYOFTHEWEEK_THURSDAY,
    DAYOFTHEWEEK_FRIDAY,
    DAYOFTHEWEEK_SATURDAY,
    DAYOFTHEWEEK_SUNDAY,
)

##############################################################################
#false data for the debug mode (if no sensor connected):
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
DEFAULT_TEMPERATURE = 5000
ERROR_TEMPERATURE = 85000
SENSOR_READING_MAX_ATTEMPTS = 4
#Each  DS18*20  contains  a  unique  ROM  code  that  is  64-bits  long.
#| The  first  8  bits  are  a  1-Wire  family code
#| DS18B20 code is 28, DS18S20 code is 10
TEMPERATURE_SENSORS_FAMILY_CODES = [10, 28]

##############################################################################
# Raspberry one wire devices folder paths:
##############################################################################
# one wire device folder is in a segment of the kernel read-write transient
# storage aka random access memory, it's not a real location, it's a pretend
# filesystem created by the kernel sysfs driver. It's effectively "ramdisk"
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
TELEINFO_TIMEOUT = 4 # [seconds]
TELEINFO_HISTORY_DELTA = 30
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
#| in position "on when on": turns on the heating when the output is on
#| in position "on when off": turns on the heating when the output is off

HEATERS_PILOTING_MODE = "on when off"

##############################################################################
# LANGUAGE
##############################################################################

WEEKDAYS = [
    DAYOFTHEWEEK_MONDAY[settings.LANGUAGE_CODE],
    DAYOFTHEWEEK_TUESDAY[settings.LANGUAGE_CODE],
    DAYOFTHEWEEK_WEDNESDAY[settings.LANGUAGE_CODE],
    DAYOFTHEWEEK_THURSDAY[settings.LANGUAGE_CODE],
    DAYOFTHEWEEK_FRIDAY[settings.LANGUAGE_CODE],
    DAYOFTHEWEEK_SATURDAY[settings.LANGUAGE_CODE],
    DAYOFTHEWEEK_SUNDAY[settings.LANGUAGE_CODE],
]

##############################################################################
# EDF
##############################################################################
PRICE_PER_KILOWATT_HOUR_HP = 0.1821
PRICE_PER_KILOWATT_HOUR_HC = 0.1360
MONTHLY_SUBSCRIPTION_PRICE = 15.42
HC_PERIODS = [( "02:00" , "07:00" ), ( "13:00" , "16:00" )]

##############################################################################
# heating need requirement
##############################################################################
# to calculate the heating requirement we make for each hour of a day the
#| difference between the outside temperature and the reference temperature
#| then we add all its differences

HEATING_NEED_REFERENCE_TEMPERATURE = 21000
