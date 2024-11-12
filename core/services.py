from result import Err, Ok, Result


def watt_to_ampere(power_watts, voltage) -> Result[float, str]:
    try:
        return Ok(power_watts / voltage)
    except ZeroDivisionError:
        return Err("Voltage must be greater than zero.")
