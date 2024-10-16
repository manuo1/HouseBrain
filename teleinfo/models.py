from django.db import models
from django.utils import timezone


class TeleinformationHistory(models.Model):
    created = models.DateTimeField()
    data = models.JSONField()

    def __str__(self):

        local_created = timezone.localtime(self.created)
        return f"{local_created:%d/%m/%Y %H:%M} {local_created.tzname()}"
