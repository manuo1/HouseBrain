from django.contrib import admin

from sensors.models import TemperatureHumiditySensor


@admin.register(TemperatureHumiditySensor)
class TemperatureHumiditySensorAdmin(admin.ModelAdmin):
    list_display = ("mac_address", "name", "created_at")
    search_fields = ("name", "mac_address")
    list_filter = ("created_at",)
    ordering = ("-created_at",)

    readonly_fields = ("mac_address", "created_at")
