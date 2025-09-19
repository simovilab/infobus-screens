from channels.generic.websocket import AsyncWebsocketConsumer
import json


class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.test_group_name = "test_group"
        await self.channel_layer.group_add(self.test_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.test_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.test_group_name, {"type": "test_message", "message": message}
        )

    async def test_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
