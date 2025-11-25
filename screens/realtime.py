from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def push_device_message(message):
    """
    Envía un mensaje a través del grupo WebSocket del dispositivo, si hay
    conexiones activas.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    group_name = f"device-{message.device_id}"

    payload = {
        "type": "device_message",
        "message_id": message.id,
        "template_code": message.template.code if message.template else None,
        "payload": message.payload,
        "status": message.status,
    }

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_message",  # llama al método send_message del consumer
            "payload": payload,
        },
    )
