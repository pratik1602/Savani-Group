from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from channels.exceptions import StopConsumer

import json

class UserNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        if self.scope["user"] is not AnonymousUser and self.scope['user'] is not None:
            await self.channel_layer.group_add("User_notification", self.channel_name)   
        else:
            await self.close()
            raise StopConsumer()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("User_notification", self.channel_name)
        raise StopConsumer()

    async def receive(self, text_data):
        await self.channel_layer.group_send(
            "User_notification", {"type": "send.message", "data": "New user register."}
        )

    async def send_message(self, event):
        await self.send(text_data=json.dumps({"data": event['data']}))