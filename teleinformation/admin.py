from django.contrib import admin

from .models import TeleinformationHistory, PowerMonitoring

""" add models to admin page """

admin.site.register(TeleinformationHistory)
admin.site.register(PowerMonitoring)
