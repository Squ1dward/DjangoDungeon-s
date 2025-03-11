import json
from channels.generic.websocket import AsyncWebsocketConsumer

class chatter(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles a new WebSocket connection."""
        self.lobby_name = self.scope["url_route"]["kwargs"]["lobby_name"]
        self.lobby_group_name = f"chat_{self.lobby_name}"

        # Green text for successful connection
        print(f"\033[92m🔵 New connection: {self.channel_name} joined {self.lobby_group_name}\033[0m")

        # Join the WebSocket group (room)
        await self.channel_layer.group_add(self.lobby_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        # Red text for disconnection
        print(f"\033[91m🔴 Disconnected: {self.channel_name} left {self.lobby_group_name}\033[0m")

        # Leave the WebSocket group (room)
        await self.channel_layer.group_discard(self.lobby_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handles messages received from WebSocket."""
        data = json.loads(text_data)
        message = data["message"]
        username = data["username"]

        # Regular message logging
        print(f"📩 Message from {username}: {message}")

        # Send message to WebSocket group
        await self.channel_layer.group_send(
            self.lobby_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username
            },
        )

    async def chat_message(self, event):
        """Sends messages to WebSocket clients."""
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event["username"]
        }))



