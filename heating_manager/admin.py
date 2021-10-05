from django.contrib import admin

from .models import HeatingMode, HeatingPeriod, CurrentHeatingMode

""" add models to admin page """

admin.site.register(HeatingMode)
admin.site.register(HeatingPeriod)
admin.site.register(CurrentHeatingMode)
