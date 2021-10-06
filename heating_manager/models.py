from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from housebrain_config.settings.messages import (
    DAYOFTHEWEEK_MONDAY as monday,
    DAYOFTHEWEEK_TUESDAY as tuesday,
    DAYOFTHEWEEK_WEDNESDAY as wednesday,
    DAYOFTHEWEEK_THURSDAY as thursday,
    DAYOFTHEWEEK_FRIDAY as friday,
    DAYOFTHEWEEK_SATURDAY as saturday,
    DAYOFTHEWEEK_SUNDAY as sunday,
)
from rooms.models import Room

class HeatingPeriodManager(models.Manager):
    def room_heating_periods(self,room):
        return HeatingPeriod.objects.filter(associated_room = room)

    def current_heating_period_setpoint_temperature(self,room):
        temperature = 0
        current_heating_period = self.current_heating_period(room)
        if current_heating_period:
            temperature = current_heating_period[0].setpoint_temperature
        return temperature

    def current_heating_period(self, room):
        now = timezone.now()
        current_heating_mode = CurrentHeatingMode.objects.all()
        if current_heating_mode:
            current_heating_mode = current_heating_mode[0].heating_mode

        heating_period = HeatingPeriod.objects.filter(
            associated_heating_mode = current_heating_mode,
            week_day = now.weekday(),
            associated_room = room,
            start_time__lt = now.time(), #lower than now
            end_time__gte = now.time() #Greater than or equal to now
        )
        return heating_period


class HeatingMode(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class HeatingPeriod(models.Model):

    class DayOfTheWeekChoices(models.IntegerChoices):
        MONDAY = 0, monday[settings.LANGUAGE_CODE]
        TUESDAY = 1, tuesday[settings.LANGUAGE_CODE]
        WEDNESDAY = 2, wednesday[settings.LANGUAGE_CODE]
        THURSDAY = 3, thursday[settings.LANGUAGE_CODE]
        FRIDAY = 4, friday[settings.LANGUAGE_CODE]
        SATURDAY = 5, saturday[settings.LANGUAGE_CODE]
        SUNDAY = 6, sunday[settings.LANGUAGE_CODE]

    week_day = models.IntegerField(
        default=DayOfTheWeekChoices.MONDAY,
        choices=DayOfTheWeekChoices.choices
        )
    start_time = models.TimeField()
    end_time = models.TimeField()
    setpoint_temperature = models.IntegerField(default=5)
    associated_room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    associated_heating_mode = models.ForeignKey(
        HeatingMode,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    def __str__(self):
        ret = "{} | {} - {} ( {} -> {} ) {}°C".format(
            self.associated_heating_mode.name,
            self.DayOfTheWeekChoices.choices[self.week_day][1] ,
            self.associated_room.name,
            self.start_time,
            self.end_time,
            self.setpoint_temperature,
        )
        return ret

class CurrentHeatingMode(models.Model):
    heating_mode = models.OneToOneField(
        HeatingMode,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    def __str__(self):
        return f'Current : {self.heating_mode.name}'
