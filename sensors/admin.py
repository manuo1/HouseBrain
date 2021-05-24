from django.contrib import admin

from .models import TemperatureSensor, TemperatureHistory

""" add models to admin page """

admin.site.register(TemperatureSensor)
admin.site.register(TemperatureHistory)
