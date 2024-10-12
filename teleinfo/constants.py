import os
import serial

UNPLUGGED_MODE = os.getenv("UNPLUGGED_MODE", "False") == "True"

"""Raspberry serial port config"""
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyS0")
SERIAL_BAUDRATE = 1200
SERIAL_PARITY = serial.PARITY_NONE
SERIAL_STOPBITS = serial.STOPBITS_ONE
SERIAL_BYTESIZE = serial.SEVENBITS
SERIAL_TIMEOUT = 1  # 1 seconde

INVALIDE_KEY = "invalid"

FIRST_TELEINFO_FRAME_KEY = "ADCO"
LAST_TELEINFO_FRAME_KEY = "MOTDETAT"
