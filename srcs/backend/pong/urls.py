# pong/urls.py
from django.urls import path, re_path, include
from channels.routing import ProtocolTypeRouter  # Import ProtocolTypeRouter
from channels.routing import URLRouter
from .views import pong_game
from .consumers import GameConsumer

websocket_urlpatterns = [
    re_path(r'ws/pong/$', GameConsumer.as_asgi()),
    # Add more paths for different WebSocket consumers if needed
]

application = ProtocolTypeRouter(
    {
        "websocket": URLRouter(websocket_urlpatterns),
        # Add other protocols if needed (e.g., http)
    }
)

urlpatterns = [
    path('', pong_game, name='pong_game'),
]
