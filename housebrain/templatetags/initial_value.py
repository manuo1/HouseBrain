from django import template
from datetime import datetime

register = template.Library()

@register.filter(name='initial_value_HM')
def initial_value_HM (field, arg):
    return field.as_widget(attrs={'value': arg.strftime("%H:%M")})

@register.filter(name='initial_value_temperature')
def initial_value_temperature (field, arg):
    return field.as_widget(attrs={'value': round(arg/1000)})
