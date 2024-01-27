# pong/urls.py
from django.urls import path
from .views import PaddleMoveView, InitGameView

urlpatterns = [
    path('init-game/', InitGameView.as_view(), name='init_game'),
    path('move-paddle/', PaddleMoveView.as_view(), name='move_paddle'),
]
