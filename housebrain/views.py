from django.core.paginator import Paginator
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render
from housebrain_config.settings.constants import (
    ERROR_TEMPERATURE, WEEKDAYS
)
from .forms import (
    HeatingPeriodCreateForm,
    CopyRoomForm,
    CopyWeekdayForm,
    HeatingPeriodModifyForm,
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
                    temperature_history = (t_sensor_manager.
                            seven_days_sensor_temperature_history(sensor))
                    rooms_without_heating.append(
                        {
                            "room" : room,
                            "sensor" : sensor,
                            "temperature_history" : temperature_history,
                        }
                    )

    context = {
        'dropdown_menu_heating_modes' : heating_period_manager.all_heating_modes(),
        'date_time': f'{timezone.now():%d/%m/%Y %H:%M}',
        'rooms_with_heating': rooms_with_heating,
        'rooms_without_heating': rooms_without_heating,
        'hours_list' : list(range(24)),
        'str_weekdays' : WEEKDAYS,

    }
    return render(request, 'homepage.html', context)

def heating_periods(request, heating_mode_id):
    if request.method == 'POST':

        add_heating_period = request.POST.get('add_heating_period')
        copy_room = request.POST.get('copy_room')
        copy_weekday = request.POST.get('copy_weekday')
        delete_heating_period = request.POST.get('delete_heating_period')
        modify_heating_period = request.POST.get('modify_heating_period')
        reset_room = request.POST.get('reset_room')

        if modify_heating_period:
            # modify_heating_period if formated in html like a dictionary
            modified_heating_period_data = eval(modify_heating_period)
            modify_heating_period_form = HeatingPeriodModifyForm(request.POST)
            if modify_heating_period_form.is_valid():
                modified_heating_period = {
                    'start_time': modify_heating_period_form.cleaned_data.get(
                            'start_time'
                        ),
                    'end_time': modify_heating_period_form.cleaned_data.get(
                            'end_time'
                        ),
                    'setpoint_temperature': (
                        modify_heating_period_form.cleaned_data.get(
                            'setpoint_temperature'
                        )*1000),
                    'heating_period_id': modified_heating_period_data['heating_period'],
                }
                heating_period_manager.modify_heating_period(modified_heating_period)

        if reset_room:
            reset_room = eval(reset_room)
            heating_period_manager.reset_room(
                reset_room["heating_mode"],
                reset_room["weekday"],
                reset_room["room"]
            )
        if delete_heating_period:
            delete_heating_period = eval(delete_heating_period)
            heating_period_manager.delete_heating_period(
                delete_heating_period["heating_period"]
            )

        if add_heating_period:
            add_heating_period = eval(add_heating_period)
            new_heating_period_form = HeatingPeriodCreateForm(request.POST)
            if new_heating_period_form.is_valid():
                new_heating_period = {
                    'start_time': new_heating_period_form.cleaned_data.get(
                            'start_time'
                        ),
                    'end_time': new_heating_period_form.cleaned_data.get(
                            'end_time'
                        ),
                    'setpoint_temperature': (
                        new_heating_period_form.cleaned_data.get(
                            'setpoint_temperature'
                        )*1000),
                    'str_weekday': add_heating_period['weekday'],
                    'room_id': add_heating_period['room'],
                    'heating_mode_id': add_heating_period['heating_mode'],
                }
                heating_period_manager.add_heating_period(new_heating_period)

        if copy_room:
            copied_room_data = eval(copy_room)
            pasted_room_form = CopyRoomForm(request.POST)
            if pasted_room_form.is_valid():
                pasted_rooms = pasted_room_form.cleaned_data.get('room')
                heating_period_manager.copy_room(copied_room_data, pasted_rooms)

        if copy_weekday:
            copied_weekday_data = eval(copy_weekday)
            pasted_weekday_form = CopyWeekdayForm(request.POST)
            if pasted_weekday_form.is_valid():
                pasted_weekdays = pasted_weekday_form.cleaned_data.get('weekday')
                heating_period_manager.copy_weekday(copied_weekday_data, pasted_weekdays)

    """ get mode heating_periodes"""
    heating_modes = {}
    mode = heating_period_manager.heating_mode(heating_mode_id)
    rooms = heater_manager.rooms_with_heater()
    page_list = []
    if mode and rooms:
        for int_weekday, str_weekday in enumerate(WEEKDAYS):
            rooms_heating_periods = {}
            for room in rooms:
                rooms_heating_periods.update(
                    {
                        room : heating_period_manager.
                            room_weekday_heating_periods(
                                mode, int_weekday, room
                            )
                    }
                )
            page_list.append( { mode : {str_weekday :rooms_heating_periods}} )

    """ add paginator """
    paginator = Paginator(page_list, 1)  # Show 1 day per page.
    page_number = request.GET.get('page')
    weekday_rooms_heating_periods = paginator.get_page(page_number)

    """ forms """
    create_heating_period_form = HeatingPeriodCreateForm()
    modify_heating_period_form = HeatingPeriodModifyForm()
    # Remove initial field for setpoint_temperature to allow modification
    #| of the initial value from the attrs of the model
    modify_heating_period_form.fields['setpoint_temperature'].initial = None

    copy_room_form = CopyRoomForm()
    copy_weekday_form = CopyWeekdayForm()

    rooms_with_heating_names = [
        room.name for room in heater_manager.rooms_with_heater()
    ]

    context = {
        'dropdown_menu_heating_modes' : heating_period_manager.all_heating_modes(),
        'date_time': f'{timezone.now():%d/%m/%Y %H:%M}',
        'weekdays_pages': weekday_rooms_heating_periods,
        'str_weekdays' : WEEKDAYS,
        'rooms_with_heating_names' : rooms_with_heating_names,
        'copy_weekday_form' : copy_weekday_form,
        'copy_room_form' : copy_room_form,
        'create_heating_period_form': create_heating_period_form,
        'modify_heating_period_form': modify_heating_period_form,

    }

    return render(request, 'heating_periods.html', context)
