from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from housebrain_config.settings.constants import DEFAULT_TEMPERATURE
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
        return HeatingPeriod.objects.filter(associated_room = room).order_by('week_day','start_time')

    def all_heating_modes(self):
        return HeatingMode.objects.all()

    def current_heating_period_setpoint_temperature(self,room):
        temperature = DEFAULT_TEMPERATURE
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
        associated_heating_mode_name = "None"
        if self.associated_heating_mode:
            associated_heating_mode_name = self.associated_heating_mode.name
        associated_room_name = "None"
        if self.associated_room:
            associated_room_name = self.associated_room.name

        ret = "{} | {} - {} ( {} -> {} ) {}°C".format(
            associated_heating_mode_name,
            self.DayOfTheWeekChoices.choices[self.week_day][1] ,
            associated_room_name,
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
        name = "None"
        if self.heating_mode:
            name = self.heating_mode.name
        return f'Current : {name}'
