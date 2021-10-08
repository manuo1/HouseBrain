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
    rooms_without_heating = []
    for room in room_manager.all_rooms():
        sensor = heaters = None
        # select rooms with usable data
        if room:
            # get room sensor
            sensor = t_sensor_manager.room_sensor(room)
            if sensor:
                # get room heater (first one if room have many)
                heaters = heater_manager.room_heaters(room)
                if heaters:
                    rooms_with_heating.append(
                        {
                            "room" : room,
                            "sensor" : sensor,
                            "heater" : heaters[0]
                        }
                    )
                else:
                    temperature_history = t_sensor_manager.seven_days_sensor_temperature_history(sensor)
                    rooms_without_heating.append(
                        {
                            "room" : room,
                            "sensor" : sensor,
                            "temperature_history" : temperature_history,
                        }
                    )
                    
    context = {
        'date_time': f'{timezone.now():%d/%m/%Y %H:%M}',
        'rooms_with_heating': rooms_with_heating,
        'rooms_without_heating': rooms_without_heating,
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
