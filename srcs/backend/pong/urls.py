# pong/urls.py
from django.urls import path, re_path, include
from channels.routing import ProtocolTypeRouter  # Import ProtocolTypeRouter
from channels.routing import URLRouter
from . import views
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
    path('get-ip-address/', views.get_ip_address, name='get_ip_address'),
    
    # path('init-game/', InitGameView.as_view(), name='init_game'),
    # path('populate_database/', PopulateDatabaseView.as_view(), name='populate_database'),
    # path('game-info/<int:game_id>/', GameInfoView.as_view(), name='game-info'),
    # path('move-paddle/<int:game_id>/', PaddleMoveView.as_view(), name='move_paddle'),
    # path('update-paddle/', UpdatePaddleView.as_view(), name='update_paddle'),
    # path('update-game-data/<int:game_id>/', UpdateGameDataView.as_view(), name='update_game_data'),
    # path('start-game/', StartGameView.as_view(), name='start_game'),
]

