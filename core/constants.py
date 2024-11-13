import os


UNPLUGGED_MODE = os.getenv("UNPLUGGED_MODE", "False") == "True"
DEFAULT_VOLTAGE = 230  # volts
