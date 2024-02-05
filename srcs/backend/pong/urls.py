# pong/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('init-game/', InitGameView.as_view(), name='init_game'),
    path('populate_database/', PopulateDatabaseView.as_view(), name='populate_database'),
    # path('game-info/<int:game_id>/', GameInfoView.as_view(), name='game-info'),
    # path('move-paddle/<int:game_id>/', PaddleMoveView.as_view(), name='move_paddle'),
    path('update-paddle/', UpdatePaddleView.as_view(), name='update_paddle'),
    path('update-game-data/<int:game_id>/', UpdateGameDataView.as_view(), name='update_game_data'),
]

