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
                    'start_time': forms.TimeInput(attrs={'type': 'time'}),
                    'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class CopyRoomForm(forms.Form):
    room = RoomMultipleChoiceField(
            queryset=Room.objects.all(),
            widget=forms.CheckboxSelectMultiple,
        )

class CopyWeekdayForm(forms.Form):
    weekday = forms.MultipleChoiceField(
            choices = WEEKDAYS_CHOICES,
            widget=forms.CheckboxSelectMultiple,
            )
