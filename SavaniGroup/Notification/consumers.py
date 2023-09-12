from channels.generic.websocket import  AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

import json

class AdminNotificationConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # print('Admin :',self.scope['user'])
        # print('Admin email :',self.scope['user']['is_admin'])
        if self.scope["user"] is not AnonymousUser and self.scope['user']['is_admin'] and self.scope['user'] is not None:
            await self.channel_layer.group_add("Admin_notification", self.channel_name)   
        else:
            print('connection faild...!')
            await self.close()

    async def disconnect(self, close_code):
        print('close code' , close_code)
        await self.channel_layer.group_discard("Admin_notification", self.channel_name)

    async def receive(self, text_data):

        # Send message to room group
        await self.channel_layer.group_send(
            "Admin_notification", {"type": "chat.message", "data": "New user register."}
        )

    # Receive message from room group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"data": event['data']}))