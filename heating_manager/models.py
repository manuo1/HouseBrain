from datetime import datetime
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from housebrain_config.settings.constants import (
    DEFAULT_TEMPERATURE, WEEKDAYS
)
from rooms.models import Room, RoomManager
from heaters.models import HeaterManager
room_manager = RoomManager()
heater_manager = HeaterManager()

class HeatingPeriodManager(models.Manager):

    def rooms_with_heater(self):
        rooms = []
        for room in room_manager.all_rooms():
            if heater_manager.room_heaters(room):
                rooms.append(room)
        return rooms

    def modify_heating_period(self, period):
        heating_period = self.heating_period(
                period['heating_period_id']
            )
        if heating_period:
            heating_period.start_time = period['start_time']
            heating_period.end_time = period['end_time']
            heating_period.setpoint_temperature = period[
                    'setpoint_temperature'
                ]
            heating_period.save()

    def add_heating_mode(self, heating_mode_name ):
        new_heating_mode = HeatingMode(name=heating_mode_name)
        new_heating_mode.save()

    def add_heating_period(self, period_data ):
        period_data['week_day'] = self.int_weekday(period_data['str_weekday'])
        period_data['associated_room'] = self.room(period_data['room_id'])
        period_data['associated_heating_mode'] = self.heating_mode(
                period_data['heating_mode_id'])
        del period_data['room_id']
        del period_data['str_weekday']
        del period_data['heating_mode_id']
        new_period = HeatingPeriod(**period_data)
        new_period.save()

    def copy_weekday(self, copied_weekday_ids, pasted_weekdays):
        for pasted_weekday in pasted_weekdays:
            # delete pasted_weekday heating_periods
            HeatingPeriod.objects.filter(
                associated_heating_mode = self.heating_mode(
                    copied_weekday_ids['heating_mode']
                ),
                week_day = self.int_weekday(pasted_weekday)
            ).delete()
            # duplicate copied_weekday heating_periods in pasted_weekday
            copied_weekday_heating_periods = HeatingPeriod.objects.filter(
                    associated_heating_mode = self.heating_mode(
                        copied_weekday_ids['heating_mode']
                    ),
                    week_day = self.int_weekday(copied_weekday_ids['weekday'])
                )
            for heating_period in copied_weekday_heating_periods:
                heating_period.id = None
                heating_period.week_day = self.int_weekday(pasted_weekday)
                heating_period.save()

    def copy_heating_mode( self, copied_mode_id, pasted_mode_id ):
        pasted_mode = self.heating_mode(pasted_mode_id)
        # delete pasted_mode heating_periods
        HeatingPeriod.objects.filter(
                associated_heating_mode__id = pasted_mode_id,
                ).delete()
        # get copied_mode heating_periods
        copied_mode_heating_periods = HeatingPeriod.objects.filter(
                associated_heating_mode__id = copied_mode_id,
            )
        for new_heating_period in copied_mode_heating_periods:
            new_heating_period.id = None
            new_heating_period.associated_heating_mode = pasted_mode
            new_heating_period.save()

    def copy_room(self, copied_room_ids, pasted_rooms):
        for pasted_room in pasted_rooms:
            # delete pasted_room heating_periods
            HeatingPeriod.objects.filter(
                associated_room = pasted_room,
                associated_heating_mode = self.heating_mode(
                    copied_room_ids['heating_mode']
                ),
                week_day = self.int_weekday(copied_room_ids['weekday'])
            ).delete()
            # duplicate copied_room heating_periods in pasted_room
            copied_room_heating_periods = HeatingPeriod.objects.filter(
                    associated_room = self.room(copied_room_ids['room']),
                    associated_heating_mode = self.heating_mode(
                        copied_room_ids['heating_mode']
                    ),
                    week_day = self.int_weekday(copied_room_ids['weekday'])
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
        return HeatingMode.objects.all().order_by('name')

    def all_heating_periods(self):
        return HeatingPeriod.objects.select_related().all()

    def all_heating_mode_calendar(self,*args):
        """ 
            order accept "desc" arg to to reverse the sort order.
            defaut
        """
        order_by = 'date_time_start'
        for arg in args:
            if arg == "desc":
                order_by = '-date_time_start'           
        return HeatingModeCalendar.objects.select_related().all().order_by(order_by)

    def heating_periods_for(self, heating_mode_id, str_weekday, room_id):
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

    def current_heating_period(self, room ):
        heating_period = None
        now = timezone.now()
        current_heating_mode = self.current_heating_mode()
        if current_heating_mode:
            heating_period = HeatingPeriod.objects.filter(
                associated_heating_mode = current_heating_mode,
                week_day = now.weekday(),
                associated_room = room,
                start_time__lt = now.time(), #lower than now
                end_time__gte = now.time() #Greater than or equal to now
            )
        return heating_period

    def current_heating_mode(self):
        current_heating_mode = HeatingModeCalendar.objects.filter(
            date_time_start__lt = timezone.now(), #lower than now
            date_time_end__gte = timezone.now() #Greater than or equal to now
        )
        if current_heating_mode:
            current_heating_mode = current_heating_mode[0].heating_mode
        else:
            current_heating_mode = None
        return current_heating_mode

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
        return RoomHeatingModel.objects.all().order_by('name')

    def load_room_model(self, room_model_id, pasted_room_ids):
        # delete old room heating_periods
        self.heating_periods_for(
            pasted_room_ids['heating_mode'],
            pasted_room_ids['weekday'],
            pasted_room_ids['room']
        ).delete()
        # load new room heating_periods
        heating_periods = ModelHeatingPeriod.objects.filter(
            associated_room_heating_model__id = room_model_id
        )
        if heating_periods:
            for heating_period in heating_periods:
                new_heating_period = {
                    'start_time': heating_period.start_time,
                    'end_time': heating_period.end_time,
                    'setpoint_temperature': heating_period.setpoint_temperature,
                    'str_weekday': pasted_room_ids['weekday'],
                    'room_id': pasted_room_ids['room'],
                    'heating_mode_id': pasted_room_ids['heating_mode'],
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

class HeatingModeCalendar(models.Model):
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()
    heating_mode = models.ForeignKey(
        HeatingMode,
        on_delete=models.CASCADE,
    )
    def __str__(self):
        return (
            f'{self.date_time_start:%a %d/%m/%Y %H:%M}'
            f' - {self.date_time_end:%a %d/%m/%Y %H:%M}'
            f' | {self.heating_mode.name}'
        )

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
        on_delete=models.CASCADE,
    )
    associated_heating_mode = models.ForeignKey(
        HeatingMode,
        on_delete=models.CASCADE,
    )
    def save(self, *args, **kwargs):
        minutes_differences = (
            (self.end_time.hour*60 + self.end_time.minute)
            - (self.start_time.hour*60 + self.start_time.minute))
        """for beter display add one minute to change 23:59 for 24:00"""
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
