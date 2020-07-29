from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
import redis
 
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=10,
    decode_responses=True
)
conn = redis.Redis(connection_pool=pool, decode_responses=True)

# class ChatConsumer(WebsocketConsumer):

#     def connect(self):
#         async_to_sync(self.channel_layer.group_add)("chat", self.channel_name)

#     def disconnect(self, close_code):
#         async_to_sync(self.channel_layer.group_discard)("chat", self.channel_name)

#     def receive(self, text_data):
#         async_to_sync(self.channel_layer.group_send)(
#             "chat",
#             {
#                 "type": "chat.message",
#                 "text": text_data,
#             },
#         )

#     def chat_message(self, event):
#         self.send(text_data=event["text"])

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
 
 
class Tuisong(AsyncWebsocketConsumer):
    def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['room_name']
 
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
 
 
        self.accept()
 
 
 
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
 
    # 主动推送
    def tui_song(self, event):
        ggg = event['msg']
        self.send(text_data=json.dumps({
            'message': ggg
        }))