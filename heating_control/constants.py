from dataclasses import dataclass


@dataclass
class RadiatorStateChange:
    radiator_id: int
    current_state: bool
    next_state: bool
    priority: int


@dataclass
class RadiatorState:
    radiator_id: int
    is_on: bool
    priority: int


TEMPERATURE_TO_HEATING_DURATION = [
    # (T_min, T_max, heating_duration)
    (float("-inf"), -2.0, 5),
    (-2.0, -1.5, 4),
    (-1.5, -1.0, 3),
    (-1.0, -0.5, 2),
    (-0.5, +0.5, 1),
    (+0.5, float("+inf"), 0),
]
