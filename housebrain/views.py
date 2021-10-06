from django.conf import settings
from django.utils import timezone
from django.shortcuts import render
from housebrain_config.settings.constants import (ERROR_TEMPERATURE)
from housebrain_config.settings.messages import (
    DAYOFTHEWEEK_LIST as week_day_list
)
from sensors.models import TemperatureSensorManager
from heaters.models import HeaterManager
from rooms.models import RoomManager
from heating_manager.models import HeatingPeriodManager

room_manager = RoomManager()
heater_manager = HeaterManager()
t_sensor_manager = TemperatureSensorManager()
heating_period_manager = HeatingPeriodManager()

def homepage(request):

    rooms_with_heating = []
    rooms_with_temperature_sensor_only = []
    for room in room_manager.all_rooms():
        data = {}
        # select rooms with usable data
        if room:
            data["room"] = room
            # get room sensor
            sensor = t_sensor_manager.room_sensor(room)
            if sensor:
                data["sensor"] = sensor
                # get room heater (first one if room have many)
                heaters = heater_manager.room_heaters(room)
                if heaters:
                    data["heater"] = heaters[0]
                    rooms_with_heating.append(
                        rooms_with_heating_data(data)
                    )
                else:
                    rooms_with_temperature_sensor_only.append(
                        rooms_with_temperature_sensor_only_data(data)
                    )

    context = {
        'date_time': f'{timezone.now():%d/%m/%Y %H:%M}',
        'rooms_with_heating': rooms_with_heating,
        'rooms_with_temperature_sensor_only': rooms_with_temperature_sensor_only,
        'hours_list' : list(range(24))
    }
    return render(request, 'homepage.html', context)

def heating_periods(request):
    rooms_heating_periods = []
    for room in room_manager.all_rooms():
        room_data = {"room":None, "heating_periods" : []}
        if room:
            heaters = heater_manager.room_heaters(room)
            if heaters:
                room_data["room"] = room
                heating_periods = heating_period_manager.room_heating_periods(room)
                if heating_periods:
                    room_data["heating_periods"] = list(heating_periods)
                rooms_heating_periods.append(room_data)



    context = {
        'date_time': f'{timezone.now():%d/%m/%Y %H:%M}',
        'rooms_heating_periods' : rooms_heating_periods
    }
    return render(request, 'heating_periods.html', context)


def rooms_with_heating_data(data):
    room_data = {
            "id" : data["room"].id,
            "heater_state_color" : "bg-light",
            "heater_state" : "OFF",
            "name" : data["room"].name,
            "setpoint_temperature" : "",
            "measured_temperature" : "",
            }
    if data["heater"].is_on:
        room_data["heater_state"] = "ON"
        room_data["heater_state_color"] = "bg-danger"
    room_data["setpoint_temperature"] = format_temperature(
            data["room"].setpoint_temperature,0
        )
    room_data["measured_temperature"] = format_temperature(
            data["sensor"].last_measured_temperature,1
        )
    return room_data

def rooms_with_temperature_sensor_only_data(data):
    room_data = {
            "id" : data["room"].id,
            "name" : data["room"].name,
            "measured_temperature" : "",
            "temperature_history" : temperature_history(data["sensor"]),
            }
    room_data["measured_temperature"] = format_temperature(
            data["sensor"].last_measured_temperature,1
        )
    return room_data

def format_temperature(temperature, digit):
    formated_temperature = f'{(temperature/1000):.{digit}f}°'
    if temperature == ERROR_TEMPERATURE:
        formated_temperature = "-"
    return formated_temperature

def temperature_history(sensor):
    temperature_history = {
        day:[] for day in week_day_list[settings.LANGUAGE_CODE]
    }
    history = t_sensor_manager.seven_days_sensor_temperature_history(sensor)
    for save in history:
        if save.date_time.minute%60==0:
            week_day = week_day_list[settings.LANGUAGE_CODE][save.date_time.weekday()]
            data = {
                "date" : f'{save.date_time:%d/%m}',
                "time" : save.date_time.hour,
                "temperature" : format_temperature(save.temperature,1),
            }
            temperature_history[week_day].append(
                data
            )
    return temperature_history
