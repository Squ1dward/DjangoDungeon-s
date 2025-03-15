from django.urls import path
from .consumers import ChatConsumer  # Import the consumer

websocket_urlpatterns = [
    path("ws/chat/", ChatConsumer.as_asgi()),  # WebSocket route
]
