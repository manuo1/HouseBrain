from django.db import models

from django.contrib.postgres.fields import JSONField

from radiators.models import Radiator
from teleinfo.constants import Teleinfo


class ElectricityDemandExceedance(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    teleinfo_data = JSONField()
    radiator_states = JSONField()

    def __str__(self):
        return f"{self.created}"

    @classmethod
    def save_exceedance(cls, teleinfo: Teleinfo):
        exceedance_record = cls(
            teleinfo_data=teleinfo.data, radiator_states=Radiator.get_all_states()
        )
        exceedance_record.save()
