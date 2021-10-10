from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render
from housebrain_config.settings.constants import (
    ERROR_TEMPERATURE, WEEKDAYS
)
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
        'hours_list' : list(range(24)),

    }
    return render(request, 'homepage.html', context)

def heating_periods(request):
    heating_modes = {}
    modes = heating_period_manager.all_heating_modes()
    rooms = room_manager.all_rooms()
    if modes and rooms:
        for mode in modes:
            heating_modes.update({ mode: {}})
            for int_weekday, str_weekday in enumerate(WEEKDAYS):
                heating_modes[mode].update({str_weekday : {}})
                for room in rooms:
                    # add only rooms with heating
                    heaters = heater_manager.room_heaters(room)
                    if heaters:
                        heating_modes[mode][str_weekday].update(
                            {
                                room : heating_period_manager.room_weekday_heating_periods(mode, int_weekday, room)
                            }
                        )
    context = {
        'date_time': f'{timezone.now():%d/%m/%Y %H:%M}',
        'heating_modes' : heating_modes,
    }
    return render(request, 'heating_periods.html', context)
