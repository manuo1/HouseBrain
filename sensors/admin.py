from django.contrib import admin

from .models import TemperatureSensor

""" add models to admin page """

admin.site.register(TemperatureSensor)
