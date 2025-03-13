import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles a new WebSocket connection."""
        self.room_group_name = "chat_lobby"  # Global chat room

        # Add user to WebSocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handles messages received from WebSocket."""
        data = json.loads(text_data)
        username = data["username"]
        message = data["message"]

        # Broadcast the message to all connected users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "username": username,
                "message": message,
            },
        )

    async def chat_message(self, event):
        """Sends messages to WebSocket clients."""
        await self.send(text_data=json.dumps({
            "username": event["username"],
            "message": event["message"],
        }))
