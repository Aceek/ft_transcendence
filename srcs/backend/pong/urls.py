# pong/urls.py
from django.urls import path
from .views import InitGameView, GameInfoView, PaddleMoveView

urlpatterns = [
    path('init-game/', InitGameView.as_view(), name='init_game'),
    path('game-info/<int:game_id>/', GameInfoView.as_view(), name='game-info'),
    path('move-paddle/<int:game_id>/', PaddleMoveView.as_view(), name='move_paddle'),
]
