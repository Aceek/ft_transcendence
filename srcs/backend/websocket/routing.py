from django.urls import re_path
from .consumers import MatchmakingConsumer

websocket_urlpatterns = [
    re_path(r'^ws/matchmaking/(?P<room_name>\w+)/?$', MatchmakingConsumer.as_asgi()),
]