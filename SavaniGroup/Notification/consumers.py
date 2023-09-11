from channels.generic.websocket import  AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

import json

class AdminNotificationConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        if self.scope["user"] is not AnonymousUser:
            # user = self.scope['user']
            # print('scope user:',user['email'])
            await self.channel_layer.group_add("Admin_notification", self.channel_name)   
        else:
            print('connection faild...!')
            await self.close()

    async def disconnect(self, close_code):
        print('close code' , close_code)
        await self.channel_layer.group_discard("Admin_notification", self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        # text_data_json = json.loads(text_data)
        print("message :",text_data)

        # Send message to room group
        await self.channel_layer.group_send(
            "Admin_notification", {"type": "chat.message", "data": "New user register."}
        )

    # Receive message from room group
    async def chat_message(self, event):
        print('event....' , event)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"data": event['data']}))