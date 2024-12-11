from enum import StrEnum


class HeatingMode(StrEnum):
    MANUAL = "manual"
    AUTO = "auto"
    OFF = "off"


class HeatingEfficiencyCorrectionMode(StrEnum):
    MANUAL = "manual"
    AUTO = "auto"


VERY_HIGH_INTENSITY = 999999

TEMPERATURE_TO_HEATING_DURATION = [
    # (T_min, T_max, heating_duration)
    (float("-inf"), -2.0, 5),
    (-2.0, -1.5, 4),
    (-1.5, -1.0, 3),
    (-1.0, -0.5, 2),
    (-0.5, +0.5, 1),
    (+0.5, float("+inf"), 0),
]
