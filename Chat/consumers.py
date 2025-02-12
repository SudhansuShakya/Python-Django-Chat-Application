import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the user id from the URL
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'notifications_{self.user_id}'

        # Join a room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, close_code):
        # Leave the conversation group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # receive notification from Websocket and broadcast it
    async def receive(self, text_data):
        # Handle the incoming message
        # text_data_json = json.loads(text_data)
        print("text_data_json==",text_data)
        message = text_data['message']
        time = text_data['time']
        sender = text_data['sender']

        # # Save the message to the database
        # conversation = await database_sync_to_async(Chat.objects.get)(id=self.chat_id)
        # message = await self.save_message(self.user, conversation, message_content)

        # Send the message to Wensocket
        await self.send(text_data=json.dumps({
            'message': message,
            'time': time,
            'sender': sender
        }))
        
    # async def send_notification(self, event):
    #     print("event==",event)
        
    #     # Send notification to WebSocket
    #     await self.send(text_data=json.dumps({
    #         'message': event['message']
    #     }))
    # Method to send notifications to a specific user
    @database_sync_to_async
    def get_user(self):
        print("Get User==",self.user_id)
        return User.objects.get(id=self.user_id)

    # @database_sync_to_async
    # def save_message(self, user, conversation, content):
    #     """Save a new message to the database"""
    #     return Message.objects.create(sender=user, chat=conversation, content=content)
