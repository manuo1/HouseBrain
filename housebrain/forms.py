from django import forms
from heating_manager.models import HeatingPeriod
from rooms.models import Room


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

class CopyRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name']
        labels = {
            'name' : 'Pièce de destination'
        }

class CopyWeekdayForm(forms.Form):
    weekday = forms.CharField(max_length=10)
