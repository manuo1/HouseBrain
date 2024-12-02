from django.contrib import admin

from sensors.constants import BLUETOOTH_SCAN_DURATION
from sensors.models import TemperatureHumiditySensor
from sensors.tasks import scan_and_update_bluetooth_bthome_th_sensors


@admin.action(description="Update all sensors")
def update_all_sensors(modeladmin, request, queryset):
    scan_and_update_bluetooth_bthome_th_sensors.delay()
    modeladmin.message_user(
        request,
        f"Les capteurs seront mit à jour dans {BLUETOOTH_SCAN_DURATION} secondes",
    )


@admin.register(TemperatureHumiditySensor)
class TemperatureHumiditySensorAdmin(admin.ModelAdmin):
    list_display = ("mac_address", "name", "temperature", "rssi")
    search_fields = ("name", "mac_address")
    list_filter = ("created_at",)
    ordering = ("mac_address",)
    readonly_fields = ("mac_address", "created_at")
    actions = [update_all_sensors]
