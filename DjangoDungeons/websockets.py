from django.urls import path
from .consumers import chatter

# WebSocket URL patterns (directly inside DjangoDungeons)
websocket_urlpatterns = [
    path("ws/chat/<str:lobby_name>/", chatter.as_asgi()),  # WebSocket chat route
]
