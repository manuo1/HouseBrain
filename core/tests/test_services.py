from datetime import datetime
from core.constants import DEFAULT_VOLTAGE
from core.services import is_new_hour, watt_to_ampere
import pytest
from result import Ok, Err


@pytest.mark.parametrize(
    "power_watts, voltage, expected",
    [
        (2300, DEFAULT_VOLTAGE, Ok(10.0)),
        (0, DEFAULT_VOLTAGE, Ok(0.0)),
        (100, 0, Err("Voltage can't be zero.")),
    ],
)
def test_watt_to_ampere(power_watts, voltage, expected):
    result = watt_to_ampere(power_watts, voltage)
    assert result == expected


@pytest.mark.parametrize(
    "old_datetime, new_datetime, expected",
    [
        (
            "not a datetime",
            datetime(2023, 11, 10, 14, 0),
            Err("'old_datetime' and 'new_datetime' must be of type 'datetime'."),
        ),
        (
            datetime(2024, 11, 13, 13, 0),
            datetime(2024, 11, 13, 13, 59),
            Ok(False),
        ),
        (
            datetime(2024, 11, 13, 13, 0),
            datetime(2024, 11, 13, 14, 0),
            Ok(True),
        ),
        (
            datetime(2000, 11, 13, 13, 0),
            datetime(2024, 11, 13, 14, 0),
            Ok(True),
        ),
        (
            datetime(2024, 11, 14, 13, 0),
            datetime(2024, 11, 13, 14, 0),
            Ok(False),
        ),
    ],
)
def test_is_new_hour(old_datetime, new_datetime, expected):
    assert is_new_hour(old_datetime, new_datetime) == expected
