from django.conf import settings
from django.db import models, IntegrityError
from django.utils import timezone
from datetime import datetime, timedelta
from housebrain_config.settings.constants import (
)
from housebrain_config.settings.messages import (
    NO_ASSOCIATED_ROOM,
    UNNAMED_SENSOR,
    LAST_TEMPERATURE_MEASUREMENT,
)
from rooms.models import Room

class TemperatureSensorManager(models.Manager):

    def seven_days_sensor_temperature_history(self,sensor):
        now = timezone.now()
        weekdays = {
            (now.date() - timedelta(days=6)) : [],
            (now.date() - timedelta(days=5)) : [],
            (now.date() - timedelta(days=4)) : [],
            (now.date() - timedelta(days=3)) : [],
            (now.date() - timedelta(days=2)) : [],
            (now.date() - timedelta(days=1)) : [],
            now.date() : [],
        }
        seven_days_before = list(weekdays.keys())[0]
        temperature_history = TemperatureHistory.objects.filter(
                associated_sensor = sensor,
                date_time__range=(seven_days_before,now),
                date_time__minute=0,
            ).order_by('date_time')
        for history in temperature_history:
            weekdays[history.date_time.date()].append(history)
        return weekdays

    def room_sensor(self, room):
        sensor = TemperatureSensor.objects.filter(associated_room=room.id)
        if not sensor:
            sensor = [None]
        return sensor[0]

    def add_sensors(self, sensor_folder_paths):
        for path in sensor_folder_paths:
            temperature_sensor = TemperatureSensor(sensor_folder_path = path)
            try:
                temperature_sensor.save()
            except IntegrityError:
                pass

    def all_sensors(self):
        list = TemperatureSensor.objects.all().order_by(
            'name', 'sensor_folder_path'
        )
        return list

    def save_temperature_history(self):
        for sensor in self.all_sensors():
            new_temperature_history = TemperatureHistory(
                temperature = sensor.last_measured_temperature,
                associated_sensor = sensor
            )
            new_temperature_history.save()

    def save_temperature(self, new_temperature, sensor):
        # update sensor measured temperatures
        sensor.previous_measured_temperature = (
            sensor.last_measured_temperature)
        sensor.last_measured_temperature = new_temperature
        sensor.save()

    def sensor_temperatures_list(self, sensor):
        sensor_temperatures_list = TemperatureHistory.objects.filter(
            associated_sensor=sensor).order_by('-date_time')
        return sensor_temperatures_list

    def add_an_error(self,sensor):
        sensor.consecutive_errors +=1
        sensor.cumulative_errors +=1
        sensor.is_malfunctioning = True
        sensor.save()

    def reset_consecutive_errors(self, sensor):
        if sensor.consecutive_errors != 0:
            sensor.consecutive_errors = 0
            if sensor.is_malfunctioning:
                sensor.is_malfunctioning = False
            sensor.save()

    def clear_all_temperature_history(self):
        TemperatureHistory.objects.all().delete()

class TemperatureSensor(models.Model):
    """ temperature sensors model """
    name = models.CharField(
        default=UNNAMED_SENSOR[settings.LANGUAGE_CODE],
        max_length=100
    )
    sensor_folder_path = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
    )
    associated_room = models.OneToOneField(
        Room,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    date_time_update = models.DateTimeField(auto_now=True)
    last_measured_temperature = models.IntegerField(
        default=ERROR_TEMPERATURE
    )
    previous_measured_temperature = models.IntegerField(
        default=ERROR_TEMPERATURE
    )
    consecutive_errors = models.IntegerField(default=0)
    cumulative_errors = models.IntegerField(default=0)
    is_malfunctioning = models.BooleanField(default=False)

    def __str__(self):
        room_name = NO_ASSOCIATED_ROOM[settings.LANGUAGE_CODE]
        if self.associated_room:
            room_name = self.associated_room.name
        ret = "{} | {} ({}) ({} : {} = {}) -  ( {} - {} )".format(
            room_name,
            self.name,
            self.sensor_folder_path[-15:],
            LAST_TEMPERATURE_MEASUREMENT[settings.LANGUAGE_CODE],
            f'{self.date_time_update:%d/%m/%Y %H:%M}',
            self.last_measured_temperature,
            self.consecutive_errors,
            self.cumulative_errors,
        )
        return ret

class TemperatureHistory(models.Model):
    """ save temperature and date_time from a temperature sensor """
    temperature = models.IntegerField()
    date_time = models.DateTimeField(auto_now_add=True)
    associated_sensor = models.ForeignKey(
        TemperatureSensor,
        on_delete=models.CASCADE
    )

    def __str__(self):
        room_name = NO_ASSOCIATED_ROOM[settings.LANGUAGE_CODE]
        if self.associated_sensor.associated_room:
            room_name = self.associated_sensor.associated_room.name

        ret = "{} | {} ({}) | {} | {}".format(
            room_name,
            self.associated_sensor.name,
            self.associated_sensor.sensor_folder_path[-15:],
            f'{self.date_time:%d/%m/%Y %H:%M}',
            f'{(self.temperature/1000):.2f}°C',
        )
        return ret
