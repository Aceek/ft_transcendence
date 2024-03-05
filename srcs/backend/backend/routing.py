from django.urls import re_path
from websocket.consumers import MatchmakingConsumer
from pong.consumers.consumers import GameConsumer
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    # matchmaking path
    re_path(r'^ws/matchmaking/?$', MatchmakingConsumer.as_asgi()),

    # pong paths
    re_path(r"ws/pong/(?P<mode>online)/(?P<players>[2-4])/(?P<type>standard)/(?P<uid>[A-Fa-f0-9\-]+)/$", GameConsumer.as_asgi(), name='online_standard_game'),
    re_path(r"ws/pong/(?P<mode>online)/(?P<players>2)/(?P<type>tournament)/(?P<tournament_id>[A-Fa-f0-9\-]+)/(?P<uid>[A-Fa-f0-9\-]+)/$", GameConsumer.as_asgi(), name='online_tournament_game'),
    re_path(r"ws/pong/(?P<mode>offline)/(?P<players>2)/(?P<type>standard)/(?P<uid>[A-Fa-f0-9\-]+)/$", GameConsumer.as_asgi(), name='offline_standard_game'),

    # chat path
    re_path(r'ws/chat/?$', ChatConsumer.as_asgi()),
]