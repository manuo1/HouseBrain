from result import Err, Ok, Result

from heating_control.constants import RadiatorState, RadiatorStateChange


def remove_the_unchanged_radiator(
    radiators_with_states: list[RadiatorStateChange],
) -> Result[list[RadiatorState], str]:
    if not isinstance(radiators_with_states, list):
        return Err("radiators_with_states must be a list")
    if not all(
        [
            isinstance(radiator_data, RadiatorStateChange)
            for radiator_data in radiators_with_states
        ]
    ):
        return Err("radiators_with_states contains incorrect data")
    return Ok(
        RadiatorState(
            radiator_id=radiator_states.radiator_id,
            is_on=radiator_states.next_state,
            priority=radiator_states.priority,
        )
        for radiator_states in radiators_with_states
        if radiator_states.current_state != radiator_states.next_state
    )
