from django.urls import re_path
from websocket.consumers import MatchmakingConsumer
from pong.consumers.consumers import GameConsumer
from chat.consumers import ChatConsumer
from user_activity_websocket.consumers import UserActivityConsumer

uuid_pattern = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"

websocket_urlpatterns = [
    # matchmaking path
    re_path(r'^ws/matchmaking/?$', MatchmakingConsumer.as_asgi()),

    # pong paths
    re_path(fr"ws/pong/(?P<mode>online)/(?P<players>[2-4])/(?P<type>standard)/(?P<room_id>{uuid_pattern})/$", GameConsumer.as_asgi(), name='online_standard_game'),
    re_path(fr"ws/pong/(?P<mode>online)/(?P<players>2)/(?P<type>tournament)/(?P<tournament_id>{uuid_pattern})/(?P<match_id>{uuid_pattern})/(?P<room_id>{uuid_pattern})/$", GameConsumer.as_asgi(), name='online_tournament_game'),
    re_path(fr"ws/pong/(?P<mode>offline)/(?P<players>2)/(?P<type>standard)/(?P<room_id>{uuid_pattern})/$", GameConsumer.as_asgi(), name='offline_standard_game'),

    # chat path
    re_path(r'ws/chat/?$', ChatConsumer.as_asgi()),

    # user activity path
    re_path(r'ws/user_activity/?$', UserActivityConsumer.as_asgi()),
]