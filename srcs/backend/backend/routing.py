from django.urls import re_path
from websocket.consumers import MatchmakingConsumer
from pong.consumers import GameConsumer
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/matchmaking/?$', MatchmakingConsumer.as_asgi()),
    # re_path(r'ws/pong/$', GameConsumer.as_asgi()),
    re_path(r"ws/pong/(?P<uid>[A-Fa-f0-9\-]+)/$", GameConsumer.as_asgi()),
    # chat path
    re_path(r'ws/chat/?$', ChatConsumer.as_asgi()),
]