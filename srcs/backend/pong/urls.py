# pong/urls.py
from django.urls import path
from .views import PaddleMoveView

urlpatterns = [
    path('move-paddle/', PaddleMoveView.as_view(), name='move_paddle'),
]