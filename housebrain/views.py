from django.utils import timezone
from django.shortcuts import render

from sensors.models import TemperatureSensorManager

t_sensor_manager = TemperatureSensorManager()

def homepage(request):
    temperatures = []
    for sensor, temperature in t_sensor_manager.all_last_temperatures():
        if sensor.associated_room:
            name = sensor.associated_room.name
        else :
            name =f'{sensor.name} ({sensor.sensor_folder_path[-15:]})'

        temperatures.append(
            (name , f'{(temperature/1000):.2f}°C')
        )
    context = {
        'date_time': f'{timezone.now():%d/%m/%Y %H:%M}',
        'temperatures': temperatures,
    }
    return render(request, 'homepage.html', context)
