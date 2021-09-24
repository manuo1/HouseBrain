from django.core import management
from django.db import models
from django.db.models.signals import post_save
from rooms.models import Room

class HeaterManager(models.Manager):

    def all_heaters(self):
        list = Heater.objects.all()
        return list

    def turn_on(self, heater):
        heater.is_on = True
        heater.save()

    def turn_off(self, heater):
        heater.is_on = False
        heater.save()

    def turn_off_all_heaters(self):
        if Heater.objects.exists():
            for heater in self.all_heaters():
                self.turn_off(heater)


class Heater(models.Model):

    class ControlPinChoices(models.IntegerChoices):
        PIN_00 = 0, 'Pin 0'
        PIN_01 = 1, 'Pin 1'
        PIN_02 = 2, 'Pin 2'
        PIN_03 = 3, 'Pin 3'
        PIN_04 = 4, 'Pin 4'
        PIN_05 = 5, 'Pin 5'
        PIN_06 = 6, 'Pin 6'
        PIN_07 = 7, 'Pin 7'
        PIN_08 = 8, 'Pin 8'
        PIN_09 = 9, 'Pin 9'
        PIN_10 = 10, 'Pin 10'
        PIN_11 = 11, 'Pin 11'
        PIN_12 = 12, 'Pin 12'
        PIN_13 = 13, 'Pin 13'
        PIN_14 = 14, 'Pin 14'
        PIN_15 = 15, 'Pin 15'



    name = models.CharField(max_length=100)
    maximum_power_consumption = models.IntegerField()
    control_pin = models.IntegerField(
        unique=True,
        blank=True,
        null=True,
        choices=ControlPinChoices.choices
        )
    is_on = models.BooleanField(default=False)
    associated_room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
         blank=True,
         null=True,
        )

    def __str__(self):
        state = "OFF"
        if self.is_on is True:
            state = "ON"

        return self.name + " : " + state

"""
    django.db.models.signals.post_save
    Use Django signals sent at the end of a model’s save() method.
    Every change on Heater objects will run update_heater_state commande
    to update the real state of the heaters
"""
def update_real_heater_state(sender, instance, created, **kwargs):
    management.call_command('update_heater_state')
post_save.connect(update_real_heater_state, sender=Heater)
