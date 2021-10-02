from django.utils import timezone
from django.shortcuts import render

from sensors.models import TemperatureSensorManager
from heaters.models import HeaterManager

heater_manager = HeaterManager()
t_sensor_manager = TemperatureSensorManager()

def homepage(request):
    temperatures = []
    heaters_state = "?"

    for sensor in t_sensor_manager.all_sensors():
        if not sensor.last_measured_temperature:
            temperature = 85000
        if sensor.associated_room:
            name = sensor.associated_room.name
            heaters = heater_manager.room_heaters(sensor.associated_room)
            setpoint_temperature = sensor.associated_room.setpoint_temperature
            if heaters:
                if heaters[0].is_on:
                    heaters_state = "ON"
                elif not heaters[0].is_on:
                    heaters_state = "OFF"
        else :
            name =f'{sensor.name} ({sensor.sensor_folder_path[-15:]})'
        temperatures.append(
            (f'( {heaters_state} ) {name} consigne : {(setpoint_temperature/1000):.2f}' ,
            f'mesure : {(sensor.last_measured_temperature/1000):.2f}°C')
        )
    context = {
        'date_time': f'{timezone.now():%d/%m/%Y %H:%M}',
        'temperatures': temperatures,
    }
    return render(request, 'homepage.html', context)
