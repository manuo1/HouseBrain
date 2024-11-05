from django.contrib import admin

from radiators.models import Radiator


@admin.register(Radiator)
class RadiatorAdmin(admin.ModelAdmin):
    list_display = ("name", "power", "priority", "control_pin", "is_on")
    list_editable = ("is_on",)
