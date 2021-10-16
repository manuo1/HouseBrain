from django import template
from datetime import datetime

register = template.Library()

@register.filter(name='initial_value_HM')
def initial_value_HM (form_field, arg):
    return form_field.as_widget(attrs={'value': arg.strftime("%H:%M")})

@register.filter(name='initial_value_temperature')
def initial_value_temperature (form_field, arg):
    return form_field.as_widget(attrs={'value': round(arg/1000)})
