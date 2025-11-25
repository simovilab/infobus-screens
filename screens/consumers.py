import json
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .models import Device, DeviceMessage

class PingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WS PING CONNECT path:", self.scope.get("path"))
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {
                    "type": "welcome",
                    "message": "ping-ok",
                }
            )
        )

    async def receive(self, text_data=None, bytes_data=None):
        # Eco sencillo
        if text_data:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "echo",
                        "received": text_data,
                    }
                )
            )

class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # device_id viene de la ruta ws/devices/<device_id>/
        self.device_id = self.scope["url_route"]["kwargs"]["device_id"]

        print("WS DEVICE CONNECT path:", self.scope.get("path"))
        print("WS DEVICE CONNECT device_id:", self.device_id)

        # Leemos el token del querystring: ?token=...
        query_string = self.scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_list = params.get("token", [])
        self.token = token_list[0] if token_list else None

        # Validar device + token
        try:
            device = await sync_to_async(Device.objects.get)(id=self.device_id)
        except Device.DoesNotExist:
            await self.close(code=4001)
            return

        if not self.token or self.token != device.auth_token:
            await self.close(code=4003)
            return

        self.device = device
        self.group_name = f"device-{self.device_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await sync_to_async(self._update_last_seen)()
        await self.accept()

        await self.send(
            text_data=json.dumps(
                {
                    "type": "welcome",
                    "device_id": self.device_id,
                }
            )
        )

    def _update_last_seen(self):
        self.device.last_seen_at = timezone.now()
        self.device.save(update_fields=["last_seen_at"])

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get("type")

        if msg_type == "heartbeat":
            await sync_to_async(self._update_last_seen)()
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "heartbeat_ack",
                        "ts": timezone.now().isoformat(),
                    }
                )
            )
        elif msg_type == "ack":
            ids = data.get("delivered_ids", [])
            if not isinstance(ids, list):
                return

            now = timezone.now()
            await sync_to_async(self._mark_delivered)(ids, now)
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "ack_ok",
                        "updated": len(ids),
                    }
                )
            )

    def _mark_delivered(self, ids, now):
        DeviceMessage.objects.filter(
            device=self.device,
            id__in=ids,
        ).update(
            status=DeviceMessage.Status.DELIVERED,
            delivered_at=now,
        )

    async def send_message(self, event):
        payload = event.get("payload", {})
        await self.send(text_data=json.dumps(payload))