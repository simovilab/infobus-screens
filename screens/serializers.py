from rest_framework import serializers

from .models import (
    DeviceGroup,
    Device,
    DistributionChannel,
    ScreenTemplate,
    DeviceMessage,
)

class DeviceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceGroup
        fields = "__all__"


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"
        read_only_fields = ("last_seen_at", "last_ip", "created_at", "updated_at")


class DistributionChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionChannel
        fields = "__all__"


class ScreenTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreenTemplate
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class DeviceMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceMessage
        fields = "__all__"