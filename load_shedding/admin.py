from django.contrib import admin

from load_shedding.models import ElectricityDemandExceedance


@admin.register(ElectricityDemandExceedance)
class ElectricityDemandExceedanceAdmin(admin.ModelAdmin):
    list_display = ("created", "short_teleinfo_data", "short_radiator_states")
    list_filter = ("created",)
    search_fields = ("teleinfo_data", "radiator_states")
    ordering = ("-created",)
    readonly_fields = ("created", "teleinfo_data", "radiator_states")

    def short_teleinfo_data(self, obj):
        return (
            str(obj.teleinfo_data)[:50] + "..."
            if len(str(obj.teleinfo_data)) > 50
            else obj.teleinfo_data
        )

    short_teleinfo_data.short_description = "Teleinfo Data"

    def short_radiator_states(self, obj):
        return (
            str(obj.radiator_states)[:50] + "..."
            if len(str(obj.radiator_states)) > 50
            else obj.radiator_states
        )

    short_radiator_states.short_description = "Radiator States"
