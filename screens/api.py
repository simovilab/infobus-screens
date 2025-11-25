from django.utils import timezone
from django.db import models

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import (
    DeviceGroup,
    Device,
    DistributionChannel,
    ScreenTemplate,
    DeviceMessage,
)
from .serializers import (
    DeviceGroupSerializer,
    DeviceSerializer,
    DistributionChannelSerializer,
    ScreenTemplateSerializer,
    DeviceMessageSerializer,
)

class DeviceGroupViewSet(viewsets.ModelViewSet):
    queryset = DeviceGroup.objects.all()
    serializer_class = DeviceGroupSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    @action(detail=True, methods=["post"])
    @action(detail=True, methods=["post"])
    def heartbeat(self, request, pk=None):
        """
        Endpoint para que el dispositivo reporte que sigue vivo.
        Ahora requiere un token de dispositivo válido.
        """
        device = self.get_object()
        self._check_device_token(request, device)

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
    
    def _check_device_token(self, request, device):
        token = request.headers.get("X-DEVICE-TOKEN")
        if not token:
            # Por compatibilidad con Django si algún día usamos META
            token = request.META.get("HTTP_X_DEVICE_TOKEN")

        if not token or token != device.auth_token:
            raise PermissionDenied("Invalid or missing device token.")
        
    @action(detail=True, methods=["get"])
    def pending_messages(self, request, pk=None):
        """
        Devuelve mensajes pendientes para este dispositivo.
        Solo mensajes con status=PENDING y que ya están listos según next_attempt_at.
        """
        device = self.get_object()
        self._check_device_token(request, device)

        now = timezone.now()
        qs = DeviceMessage.objects.filter(
            device=device,
            status=DeviceMessage.Status.PENDING,
        ).filter(
            models.Q(next_attempt_at__isnull=True) | models.Q(next_attempt_at__lte=now)
        ).order_by("created_at")[:50]  # límite básico

        serializer = DeviceMessageSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def ack_messages(self, request, pk=None):
        """
        El dispositivo notifica qué mensajes ya fueron entregados/mostrados.
        Body esperado: {"delivered_ids": [1, 2, 3]}
        """
        device = self.get_object()
        self._check_device_token(request, device)

        ids = request.data.get("delivered_ids", [])
        if not isinstance(ids, list):
            return Response(
                {"detail": "delivered_ids must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        updated = (
            DeviceMessage.objects.filter(device=device, id__in=ids)
            .update(
                status=DeviceMessage.Status.DELIVERED,
                delivered_at=now,
            )
        )

        return Response({"updated": updated}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"])
    def config(self, request, pk=None):
        """
        Devuelve la configuración efectiva para este dispositivo:
        - Datos del device
        - Grupo y canales activos
        - Template que debe usar
        - Env vars combinadas (group -> channels -> device)
        """
        device = self.get_object()
        self._check_device_token(request, device)

        group = device.group
        channels = device.channels.filter(is_active=True)

        # Merge de configs
        env = {}

        def merge_cfg(cfg):
            if isinstance(cfg, dict):
                env.update(cfg)

        # 1) Config del grupo
        if group:
            merge_cfg(group.config)

        # 2) Config de cada canal (en orden)
        for ch in channels:
            merge_cfg(ch.config)

        # 3) Config específica del device (tiene prioridad)
        merge_cfg(device.config)

        # Selección de template:
        # a) Si el device tiene uno asociado y está activo, usar ese
        # b) Si no, tomar el primero default_template activo en sus canales
        screen_template = None
        if device.screen_template and device.screen_template.is_active:
            screen_template = device.screen_template
        else:
            for ch in channels:
                if ch.default_template and ch.default_template.is_active:
                    screen_template = ch.default_template
                    break

        device_data = DeviceSerializer(device).data
        group_data = DeviceGroupSerializer(group).data if group else None
        channels_data = DistributionChannelSerializer(channels, many=True).data
        template_data = (
            ScreenTemplateSerializer(screen_template).data
            if screen_template
            else None
        )

        return Response(
            {
                "device": device_data,
                "group": group_data,
                "channels": channels_data,
                "screen_template": template_data,
                "env": env,
            },
            status=status.HTTP_200_OK,
        )


class DistributionChannelViewSet(viewsets.ModelViewSet):
    queryset = DistributionChannel.objects.all()
    serializer_class = DistributionChannelSerializer


class ScreenTemplateViewSet(viewsets.ModelViewSet):
    queryset = ScreenTemplate.objects.all()
    serializer_class = ScreenTemplateSerializer
