# pong/serializers.py
from rest_framework import serializers
from .models import Game, PaddleCoordinates

class PaddleCoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaddleCoordinates
        fields = ['player_id', 'paddle_y']

class GameInfoSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()
    paddle_coordinates = PaddleCoordinatesSerializer(many=True)

