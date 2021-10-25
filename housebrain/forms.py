from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from heating_manager.models import (
    HeatingMode,
    HeatingPeriod,
    RoomHeatingModel,
    HeatingPeriodManager,
)
from rooms.models import Room
from housebrain_config.settings.constants import (
    WEEKDAYS
)
WEEKDAYS_CHOICES = [ (day, day) for day in WEEKDAYS ]
heating_period_manager = HeatingPeriodManager()

class RoomHeatingModelCreateForm(forms.ModelForm):
    class Meta:
        model = RoomHeatingModel
        fields = ['name']
        labels = {'name': 'Nom',}
        widgets = {
                    'name': forms.TextInput(attrs={
                            'class': 'form-control text-center',
                        }),
        }

class RoomMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class HeatingModeCreateForm(forms.ModelForm):
    class Meta:
        model = HeatingMode
        fields = ['name']
        labels = {'name': 'Nom',}
        widgets = {
                    'name': forms.TextInput(attrs={
                            'class': 'form-control text-center',
                        }),
        }


class HeatingPeriodCreateForm(forms.ModelForm):
    class Meta:
        model = HeatingPeriod
        fields = ['start_time', 'end_time', 'setpoint_temperature']
        labels = {
            'start_time': 'Heure de Début',
            'end_time': 'Heure de fin',
            'setpoint_temperature': 'Température de consigne',
        }
        widgets = {
            'start_time': forms.TimeInput(attrs={
                    'type': 'time',
                    'class': 'form-control text-center',
                    'value': '00:00',
                }),
            'end_time': forms.TimeInput(attrs={
                    'type': 'time',
                    'class': 'form-control text-center',
                    'value': '00:00',
                }),
            'setpoint_temperature': forms.NumberInput(attrs={
                    'class': 'form-control text-center',
                }),
        }

class HeatingPeriodModifyForm(forms.ModelForm):
    class Meta:
        model = HeatingPeriod
        fields = ['start_time', 'end_time', 'setpoint_temperature']
        labels = {
            'start_time': 'Heure de Début',
            'end_time': 'Heure de fin',
            'setpoint_temperature': 'Température de consigne',
        }
        widgets = {
                    'start_time': forms.TimeInput(attrs={
                            'type': 'time',
                            'class': 'form-control text-center',
                        }),
                    'end_time': forms.TimeInput(attrs={
                            'type': 'time',
                            'class': 'form-control text-center',
                        }),
                    'setpoint_temperature': forms.NumberInput(attrs={
                            'class': 'form-control text-center',
                            'min':'5',
                            'max':'25',
                        }),
        }

class CopyRoomForm(forms.Form):
    room = RoomMultipleChoiceField(
            queryset=Room.objects.all(),
            widget= forms.CheckboxSelectMultiple(
                attrs={'class': 'form-check-input'}
            ),
        )

class HeatingModelChoiceForm(forms.Form):
    model = forms.ChoiceField()
    def __init__(self, *args, **kwargs):
        super(HeatingModelChoiceForm, self).__init__(*args, **kwargs)
        self.fields['model'] = forms.ChoiceField(
            widget=forms.RadioSelect(),
            choices = [
                (model.id, model.name ) for model in (
                    heating_period_manager.all_room_heating_model()
                )
            ]
        )

class CopyWeekdayForm(forms.Form):
    weekday = forms.MultipleChoiceField(
            choices = WEEKDAYS_CHOICES,
            widget=forms.CheckboxSelectMultiple(
                    attrs={'class': 'form-check-input'}),
                )

class ManualTemperatureForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'manual_mode_start',
            'manual_mode_end',
            'manual_setpoint_temperature'
        ]
        labels = {
            'manual_mode_start': 'Date et Heure de Début',
            'manual_mode_end': 'Date et Heure de fin',
            'manual_setpoint_temperature': 'Température',
        }
        widgets = {
                    'manual_mode_start': forms.DateTimeInput(attrs={
                            'type': 'datetime-local',
                            'class': 'form-control text-center',
                            'required': 'required',
                        }),

                    'manual_mode_end': forms.DateTimeInput(attrs={
                            'type': 'datetime-local',
                            'class': 'form-control text-center',
                            'required': 'required',
                        }),
                    'manual_setpoint_temperature': forms.NumberInput(attrs={
                            'class': 'form-control text-center',
                            'required': 'required',
                        }),

        }
