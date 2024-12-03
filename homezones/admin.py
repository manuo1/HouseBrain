from django.contrib import admin

from homezones.models import HomeZone


@admin.register(HomeZone)
class HomeZoneAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "temperature",
        "target_temperature",
        "radiator_state",
        "heating_mode",
    )
    list_filter = ("heating_mode",)
    search_fields = ("name",)
    autocomplete_fields = ("temperature_humidity_sensor", "radiator")
    fieldsets = (
        (None, {"fields": ("name", "temperature_humidity_sensor", "radiator")}),
        ("Heating Settings", {"fields": ("target_temperature", "heating_mode")}),
    )

    def temperature(self, obj):
        if obj.temperature_humidity_sensor:
            return f"{obj.temperature_humidity_sensor.temperature} °C"
        return "N/A"

    temperature.short_description = "Sensor Temperature"

    def radiator_state(self, obj):
        if obj.radiator:
            return "On" if obj.radiator.is_on else "Off"
        return "N/A"

    radiator_state.short_description = "Radiator State"
