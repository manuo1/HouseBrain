from django.db.models import Case, F, When, Value, BooleanField
from result import Ok, Result

from heating_control.constants import RadiatorStateChange
from homezones.models import HomeZone


def get_non_auto_home_zones_radiators_states() -> (
    Result[list[RadiatorStateChange], str]
):

    return Ok(
        [
            RadiatorStateChange(
                radiator_id=data[0], current_state=data[1], next_state=data[2]
            )
            for data in list(
                HomeZone.objects.exclude(heating_mode="auto")
                .exclude(radiator=None)
                .annotate(
                    current_is_on=F("radiator__is_on"),
                    next_is_on=Case(
                        When(heating_mode="manual", then=Value(True)),
                        When(heating_mode="off", then=Value(False)),
                        default=Value(None),
                        output_field=BooleanField(),
                    ),
                )
                .values_list("radiator_id", "current_is_on", "next_is_on")
            )
        ]
    )
