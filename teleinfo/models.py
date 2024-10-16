from django.db import models


class TeleinformationHistory(models.Model):
    created = models.DateTimeField()
    data = models.JSONField()

    def __str__(self):
        return f"{self.created:%d/%m/%Y %H:%M}"
