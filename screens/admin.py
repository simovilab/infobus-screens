from django.contrib import admin
from .models import DeviceGroup, Device, DistributionChannel, ScreenTemplate


@admin.register(DeviceGroup)
class DeviceGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "group_type", "code")
    search_fields = ("name", "code")


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "device_type", "group", "is_active", "last_seen_at")
    list_filter = ("device_type", "is_active", "group")
    search_fields = ("name", "auth_token")


@admin.register(DistributionChannel)
class DistributionChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    filter_horizontal = ("groups", "devices")


@admin.register(ScreenTemplate)
class ScreenTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "context", "is_active", "updated_at")
    list_filter = ("context", "is_active")
    search_fields = ("name", "code")
