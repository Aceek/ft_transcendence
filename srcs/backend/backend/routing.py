from django.urls import re_path
from websocket.consumers import MatchmakingConsumer
from pong.consumers.consumers import GameConsumer
from chat.consumers import ChatConsumer
from user_activity_websocket.consumers import UserActivityConsumer

websocket_urlpatterns = [
    re_path(r'^ws/matchmaking/?$', MatchmakingConsumer.as_asgi()),
    # re_path(r'ws/pong/$', GameConsumer.as_asgi()),
    re_path(r"ws/pong/(?P<uid>[A-Fa-f0-9\-]+)/$", GameConsumer.as_asgi()),
    # chat path
    re_path(r'ws/chat/?$', ChatConsumer.as_asgi()),

    # user activity path
    re_path(r'ws/user_activity/?$', UserActivityConsumer.as_asgi()),
]