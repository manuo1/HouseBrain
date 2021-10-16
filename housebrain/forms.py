from django import forms
from heating_manager.models import HeatingPeriod
from rooms.models import Room
from housebrain_config.settings.constants import (
    WEEKDAYS
)
WEEKDAYS_CHOICES = [ (day, day) for day in WEEKDAYS ]

class RoomMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name

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
                            'value': '20',
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
            widget= forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        )

class CopyWeekdayForm(forms.Form):
    weekday = forms.MultipleChoiceField(
            choices = WEEKDAYS_CHOICES,
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            )
