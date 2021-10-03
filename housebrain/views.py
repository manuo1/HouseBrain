from django.utils import timezone
from django.shortcuts import render
from housebrain_config.settings.constants import (ERROR_TEMPERATURE)
from sensors.models import TemperatureSensorManager
from heaters.models import HeaterManager

heater_manager = HeaterManager()
t_sensor_manager = TemperatureSensorManager()

def homepage(request):
    data = []
    heater_state = "No Heater"
    heater_state_color = ""
    setpoint_temperature = "-°C"
    measured_temperature = "-°C"


    for sensor in t_sensor_manager.all_sensors():

        if sensor.last_measured_temperature:
            measured_temperature = format_temperature(
                sensor.last_measured_temperature
                )
        else:
            measured_temperature = format_temperature(
                ERROR_TEMPERATURE
                )
        # if sensor have an associated room get data
        if sensor.associated_room:
            name = sensor.associated_room.name
            heaters = heater_manager.room_heaters(sensor.associated_room)
            setpoint_temperature = format_temperature(
                sensor.associated_room.setpoint_temperature
                )
            if heaters:
                if heaters[0].is_on:
                    heater_state = "ON"
                    heater_state_color = "bg-danger"
                elif not heaters[0].is_on:
                    heater_state = "OFF"
                    heater_state_color = ""
                else:
                    heater_state_color = ""
        # if sensor don't have  an associated room return sensor name and path
        else :
            name =f'{sensor.name} ({sensor.sensor_folder_path[-15:]})'
        room = {
                "id" : sensor.id,
                "color" : heater_state_color,
                "heater_state" : heater_state,
                "name" : name,
                "setpoint_temperature" : setpoint_temperature,
                "measured_temperature" : measured_temperature,
                }
        data.append(room)
    context = {
        'date_time': f'{timezone.now():%d/%m/%Y %H:%M}',
        'data': data,
    }
    return render(request, 'homepage.html', context)

def format_temperature(temperature):
    return f'{(temperature/1000):.2f}°C'
