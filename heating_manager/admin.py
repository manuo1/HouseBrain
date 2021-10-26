from django.contrib import admin

from .models import (
    HeatingMode,
    HeatingPeriod,
    RoomHeatingModel,
    ModelHeatingPeriod,
    HeatingModeCalendar,
)

""" add models to admin page """

admin.site.register(HeatingMode)
admin.site.register(HeatingPeriod)
admin.site.register(RoomHeatingModel)
admin.site.register(ModelHeatingPeriod)
admin.site.register(HeatingModeCalendar)
