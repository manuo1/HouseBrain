from django.core.paginator import Paginator
from datetime import timedelta
from django.conf import settings
from django.core import management
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
    ManualTemperatureForm,
    RoomHeatingModelCreateForm,
    RoomHeatingModelChoiceForm,
    HeatingModeCreateForm,
    HeatingModeChoiceForm,
 )
from sensors.models import TemperatureSensorManager
from heaters.models import HeaterManager
from rooms.models import RoomManager
from heating_manager.models import HeatingPeriodManager
from teleinformation.models import TeleinfoManager

room_manager = RoomManager()
heater_manager = HeaterManager()
t_sensor_manager = TemperatureSensorManager()
heating_period_manager = HeatingPeriodManager()
teleinfo_manager = TeleinfoManager()

def homepage(request):
    if request.method == 'POST' and request.user.is_authenticated:
        set_manual_temperature = request.POST.get('set_manual_temperature')
        delete_manual_temperature = request.POST.get(
                'delete_manual_temperature'
            )


        if delete_manual_temperature:
            room_id = int(delete_manual_temperature)
            room_manager.delete_manual_temperature_with_id(room_id)

        if set_manual_temperature:
            room_id = int(set_manual_temperature)
            manual_temperature_form = ManualTemperatureForm(request.POST)
            if manual_temperature_form.is_valid():
                manual_mode_data = {
                    'manual_mode_start':
                        manual_temperature_form.cleaned_data.get(
                            'manual_mode_start'
                        ),
                    'manual_mode_end':
                        manual_temperature_form.cleaned_data.get(
                            'manual_mode_end'
                        ),
                    'manual_setpoint_temperature':
                        manual_temperature_form.cleaned_data.get(
                            'manual_setpoint_temperature'
                        ),
                }
                room_manager.set_manual_temperature(
                    room_id, manual_mode_data
                )
                management.call_command('manage_heating_periods')
                management.call_command('manage_heaters')

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
    """ consumptions history """
    consumptions = []
    for day in list(range(8)):
        consumptions.append(
                teleinfo_manager.daily_consumption(
                    (timezone.now().date() - timedelta(days=day))
            )
        )
    """ forms """
    manual_temperature_form = ManualTemperatureForm()
    # manual_temperature_form initials values
    manual_temperature_form.fields[
            'manual_mode_start'
        ].initial = timezone.now().strftime("%Y-%m-%dT%H:%M")
    manual_temperature_form.fields[
            'manual_mode_end'
        ].initial = (
                timezone.now() + timedelta(hours=1)
            ).strftime("%Y-%m-%dT%H:%M")
    manual_temperature_form.fields[
            'manual_setpoint_temperature'
        ].initial = 21

    context = {
        'consumptions' : consumptions,
        'manual_temperature_form' : manual_temperature_form,
        'all_heating_modes' : (
            heating_period_manager.all_heating_modes()
        ),
        'date': timezone.now().date(),
        'rooms_with_heating': rooms_with_heating,
        'rooms_without_heating': rooms_without_heating,
        'hours_list' : list(range(24)),
        'str_weekdays' : WEEKDAYS,

    }
    return render(request, 'homepage.html', context)

def heating_periods(request, heating_mode_id):
    if request.method == 'POST' and request.user.is_authenticated:
        copy_heating_mode = request.POST.get('copy_heating_mode')
        add_heating_mode = request.POST.get('add_heating_mode')
        save_room_model = request.POST.get('save_room_model')
        load_room_model = request.POST.get('load_room_model')
        add_heating_period = request.POST.get('add_heating_period')
        copy_room = request.POST.get('copy_room')
        copy_weekday = request.POST.get('copy_weekday')
        delete_heating_period = request.POST.get('delete_heating_period')
        modify_heating_period = request.POST.get('modify_heating_period')

        if copy_heating_mode:
            copied_mode = eval(copy_heating_mode)
            copy_heating_mode_form = HeatingModeChoiceForm(request.POST)
            if copy_heating_mode_form.is_valid():
                pasted_mode_id = copy_heating_mode_form.cleaned_data.get('mode_id')
                heating_period_manager.copy_heating_mode(
                    copied_mode['heating_mode'], pasted_mode_id
                )

        if add_heating_mode:
            add_heating_mode_form = HeatingModeCreateForm(request.POST)
            if add_heating_mode_form.is_valid():
                heating_mode_name = add_heating_mode_form.cleaned_data.get('name')
                heating_period_manager.add_heating_mode(heating_mode_name)

        if load_room_model:
            pasted_room_ids = eval(load_room_model)
            load_room_model_form = RoomHeatingModelChoiceForm(request.POST)
            if load_room_model_form.is_valid():
                room_model_id = load_room_model_form.cleaned_data.get('model')
                heating_period_manager.load_room_model(
                    room_model_id, pasted_room_ids
                )

        if save_room_model:
            save_room_model_ids = eval(save_room_model)
            save_room_model_form = RoomHeatingModelCreateForm(request.POST)
            if save_room_model_form.is_valid():
                name = save_room_model_form.cleaned_data.get('name')
                heating_periods = (
                    heating_period_manager.heating_periods_for(
                        save_room_model_ids['heating_mode'],
                        save_room_model_ids['weekday'],
                        save_room_model_ids['room']
                    )
                )
                model = heating_period_manager.save_room_heating_model(name)
                heating_period_manager.save_model_heating_periods(
                    model, heating_periods
                )

        if modify_heating_period:
            modified_heating_period_id = eval(modify_heating_period)
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
                    'heating_period_id': modified_heating_period_id['heating_period'],
                }
                heating_period_manager.modify_heating_period(modified_heating_period)

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
            copied_room_ids = eval(copy_room)
            pasted_room_form = CopyRoomForm(request.POST)
            if pasted_room_form.is_valid():
                pasted_rooms = pasted_room_form.cleaned_data.get('room')
                heating_period_manager.copy_room(copied_room_ids, pasted_rooms)

        if copy_weekday:
            copied_weekday_ids = eval(copy_weekday)
            pasted_weekday_form = CopyWeekdayForm(request.POST)
            if pasted_weekday_form.is_valid():
                pasted_weekdays = pasted_weekday_form.cleaned_data.get('weekday')
                heating_period_manager.copy_weekday(copied_weekday_ids, pasted_weekdays)


    """ get mode heating_periods """
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
    paginator = Paginator(page_list, 1)  # Show 1 weekday per page.
    page_number = request.GET.get('page')
    weekday_rooms_heating_periods = paginator.get_page(page_number)

    """ forms """
    heating_mode_choice_form = HeatingModeChoiceForm()
    heating_mode_create_form = HeatingModeCreateForm()
    room_heating_model_create_form = RoomHeatingModelCreateForm()
    copy_room_form = CopyRoomForm()
    copy_weekday_form = CopyWeekdayForm()
    create_heating_period_form = HeatingPeriodCreateForm()
    create_heating_period_form.fields['setpoint_temperature'].initial = 21
    modify_heating_period_form = HeatingPeriodModifyForm()
    # Remove initial field for setpoint_temperature to allow modification
    #| of the initial value in the template
    modify_heating_period_form.fields['setpoint_temperature'].initial = None
    room_heating_model_choice_form = RoomHeatingModelChoiceForm()

    rooms_with_heating_names = [
        room.name for room in heater_manager.rooms_with_heater()
    ]

    context = {
        'all_heating_modes' : heating_period_manager.all_heating_modes(),
        'weekdays_pages': weekday_rooms_heating_periods,
        'str_weekdays' : WEEKDAYS,
        'rooms_with_heating_names' : rooms_with_heating_names,
        'copy_weekday_form' : copy_weekday_form,
        'copy_room_form' : copy_room_form,
        'create_heating_period_form': create_heating_period_form,
        'modify_heating_period_form': modify_heating_period_form,
        'room_heating_model_create_form': room_heating_model_create_form,
        'room_heating_model_choice_form' : room_heating_model_choice_form,
        'heating_mode_create_form' : heating_mode_create_form,
        'heating_mode_choice_form' : heating_mode_choice_form,
    }

    return render(request, 'heating_periods.html', context)

def heating_calendar(request):

    context = {
        'all_heating_modes' : heating_period_manager.all_heating_modes(),
        'all_heating_mode_calendar' : heating_period_manager.all_heating_mode_calendar()
    }
    return render(request, 'heating_calendar.html', context)
