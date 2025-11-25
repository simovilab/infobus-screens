from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import DeviceGroup, Device, DistributionChannel, ScreenTemplate
from .serializers import (
    DeviceGroupSerializer,
    DeviceSerializer,
    DistributionChannelSerializer,
    ScreenTemplateSerializer,
)


class DeviceGroupViewSet(viewsets.ModelViewSet):
    queryset = DeviceGroup.objects.all()
    serializer_class = DeviceGroupSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    @action(detail=True, methods=["post"])
    def heartbeat(self, request, pk=None):
        """
        Endpoint para que el dispositivo reporte que sigue vivo.
        Más adelante aquí validamos token, etc.
        """
        device = self.get_object()
        device.last_seen_at = timezone.now()
        device.last_ip = request.META.get("REMOTE_ADDR")
        device.save(update_fields=["last_seen_at", "last_ip"])
        return Response(
            {
                "status": "ok",
                "device_id": str(device.id),
                "last_seen_at": device.last_seen_at,
            },
            status=status.HTTP_200_OK,
        )


class DistributionChannelViewSet(viewsets.ModelViewSet):
    queryset = DistributionChannel.objects.all()
    serializer_class = DistributionChannelSerializer


class ScreenTemplateViewSet(viewsets.ModelViewSet):
    queryset = ScreenTemplate.objects.all()
    serializer_class = ScreenTemplateSerializer
