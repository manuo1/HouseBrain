from datetime import datetime
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from housebrain_config.settings.constants import (
    DEFAULT_TEMPERATURE, WEEKDAYS
)
from rooms.models import Room

class HeatingPeriodManager(models.Manager):

    def modify_heating_period(self, modified_heating_period):
        heating_period = self.heating_period(
                modified_heating_period['heating_period_id']
            )
        if heating_period:
            heating_period.start_time = modified_heating_period['start_time']
            heating_period.end_time = modified_heating_period['end_time']
            heating_period.setpoint_temperature = modified_heating_period[
                    'setpoint_temperature'
                ]
            heating_period.save()

    def add_heating_period(self, new_heating_period):
        new_heating_period = HeatingPeriod(
                week_day = self.int_weekday(new_heating_period['str_weekday']),
                start_time = new_heating_period['start_time'],
                end_time = new_heating_period['end_time'],
                setpoint_temperature = new_heating_period['setpoint_temperature'],
                associated_room = self.room(new_heating_period['room_id']),
                associated_heating_mode = self.heating_mode(new_heating_period['heating_mode_id']),
            )
        new_heating_period.save()

    def copy_weekday(self, copied_weekday_data, pasted_weekdays):
        for pasted_weekday in pasted_weekdays:
            # delete pasted_weekday heating_periods
            HeatingPeriod.objects.filter(
                associated_heating_mode = self.heating_mode(
                    copied_weekday_data['heating_mode']
                ),
                week_day = self.int_weekday(pasted_weekday)
            ).delete()
            # duplicate copied_weekday heating_periods in pasted_weekday
            copied_weekday_heating_periods = HeatingPeriod.objects.filter(
                    associated_heating_mode = self.heating_mode(
                        copied_weekday_data['heating_mode']
                    ),
                    week_day = self.int_weekday(copied_weekday_data['weekday'])
                )
            for heating_period in copied_weekday_heating_periods:
                heating_period.id = None
                heating_period.week_day = self.int_weekday(pasted_weekday)
                heating_period.save()

    def copy_room(self, copied_room_data, pasted_rooms):
        for pasted_room in pasted_rooms:
            # delete pasted_room heating_periods
            HeatingPeriod.objects.filter(
                associated_room = pasted_room,
                associated_heating_mode = self.heating_mode(
                    copied_room_data['heating_mode']
                ),
                week_day = self.int_weekday(copied_room_data['weekday'])
            ).delete()
            # duplicate copied_room heating_periods in pasted_room
            copied_room_heating_periods = HeatingPeriod.objects.filter(
                    associated_room = self.room(copied_room_data['room']),
                    associated_heating_mode = self.heating_mode(
                        copied_room_data['heating_mode']
                    ),
                    week_day = self.int_weekday(copied_room_data['weekday'])
                )
            for heating_period in copied_room_heating_periods:
                heating_period.id = None
                heating_period.associated_room = pasted_room
                heating_period.save()

    def delete_heating_period(self,heating_period_id):
        heating_period = self.heating_period(heating_period_id)
        if heating_period:
            heating_period.delete()

    def heating_period(self,heating_period_id):
        heating_period = HeatingPeriod.objects.filter( id = heating_period_id )
        if not heating_period:
            heating_period = [None]
        return heating_period[0]

    def room_model(self,room_model_id):
        room_model = RoomHeatingModel.objects.filter( id = room_model_id )
        if not room_model:
            room_model = [None]
        return room_model[0]

    def heating_mode(self, heating_mode_id):
        heating_mode = HeatingMode.objects.filter( id = heating_mode_id )
        if not heating_mode:
            heating_mode = [None]
        return heating_mode[0]

    def room(self, room_id):
        room = Room.objects.filter( id = room_id )
        if not room:
            room = [None]
        return room[0]

    def int_weekday(self, str_weekday):
        int_weekday = None
        for int_wd,str_wd in enumerate(WEEKDAYS):
            if str_wd == str_weekday:
                int_weekday = int_wd
        return int_weekday

    def room_weekday_heating_periods(self,heating_mode , weekday, room):
        room_weekday_heating_periods = HeatingPeriod.objects.filter(
                associated_room = room,
                week_day = weekday,
                associated_heating_mode = heating_mode,
                ).order_by('week_day','start_time')
        return list(room_weekday_heating_periods)

    def all_heating_modes(self):
        return HeatingMode.objects.all()

    def all_heating_periods(self):
        return HeatingPeriod.objects.select_related().all()

    def all_heating_periods_with_params(self, heating_mode_id, str_weekday, room_id):
        int_weekday = self.int_weekday(str_weekday)
        heating_periods = HeatingPeriod.objects.filter(
                associated_room__id = room_id,
                week_day = int_weekday,
                associated_heating_mode__id = heating_mode_id,
                )
        return heating_periods

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

    def save_room_heating_model(self,model_name):
        model = RoomHeatingModel(name=model_name)
        model.save()
        return model

    def save_model_heating_periods(self, model, heating_periods):
        for period in heating_periods:
            new_period = ModelHeatingPeriod(
                start_time = period.start_time,
                end_time = period.end_time,
                setpoint_temperature = period.setpoint_temperature,
                associated_room_heating_model = model,
            )
            new_period.save()

    def all_room_heating_model(self):
        return RoomHeatingModel.objects.all()

    def load_room_model(self, room_model_id, pasted_room_data):
        # delete old room heating_periods
        self.all_heating_periods_with_params(
            pasted_room_data['heating_mode'],
            pasted_room_data['weekday'],
            pasted_room_data['room']
        ).delete()
        # load new room heating_periods
        room_model = self.room_model(room_model_id)
        heating_periods = ModelHeatingPeriod.objects.filter(
            associated_room_heating_model__id = room_model_id
        )
        if heating_periods:
            for heating_period in heating_periods:
                new_heating_period = {
                    'start_time': heating_period.start_time,
                    'end_time': heating_period.end_time,
                    'setpoint_temperature': heating_period.setpoint_temperature,
                    'str_weekday': pasted_room_data['weekday'],
                    'room_id': pasted_room_data['room'],
                    'heating_mode_id': pasted_room_data['heating_mode'],
                }
                self.add_heating_period(new_heating_period)


class RoomHeatingModel(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class ModelHeatingPeriod(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    setpoint_temperature = models.IntegerField(default=0)
    associated_room_heating_model = models.ForeignKey(
        RoomHeatingModel,
        on_delete=models.CASCADE,
    )

class HeatingMode(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class HeatingPeriod(models.Model):

    class DayOfTheWeekChoices(models.IntegerChoices):
        MONDAY = 0, WEEKDAYS[0]
        TUESDAY = 1, WEEKDAYS[1]
        WEDNESDAY = 2, WEEKDAYS[2]
        THURSDAY = 3, WEEKDAYS[3]
        FRIDAY = 4, WEEKDAYS[4]
        SATURDAY = 5, WEEKDAYS[5]
        SUNDAY = 6, WEEKDAYS[6]

    week_day = models.IntegerField(
        default=DayOfTheWeekChoices.MONDAY,
        choices=DayOfTheWeekChoices.choices
        )
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_percentage = models.FloatField(default=0)
    setpoint_temperature = models.IntegerField(default=0)
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
    def save(self, *args, **kwargs):
        minutes_differences = (
            (self.end_time.hour*60 + self.end_time.minute)
            - (self.start_time.hour*60 + self.start_time.minute))
        """for beter display add one minute to change 23:59 like 24:00"""
        if self.end_time == 23 and self.end_time == 59:
            minutes_differences += 1
        self.day_percentage = (minutes_differences*100)/1439
        """ even displays periods less than 1% """
        if self.day_percentage < 1:
            self.day_percentage = 1
        super().save(*args, **kwargs)


    def __str__(self):
        associated_heating_mode_name = "None"
        if self.associated_heating_mode:
            associated_heating_mode_name = self.associated_heating_mode.name
        associated_room_name = "None"
        if self.associated_room:
            associated_room_name = self.associated_room.name

        ret = "{} | {} | {} ( {} -> {} ) {}°C".format(
            associated_heating_mode_name,
            associated_room_name,
            self.DayOfTheWeekChoices.choices[self.week_day][1],
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
