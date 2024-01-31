# pong/serializers.py
from rest_framework import serializers
from .models import *

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['player_id', 'score', 'paddle_y']

class BallCoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BallCoordinates
        fields = ['x', 'y']

class GameSerializer(serializers.ModelSerializer):
    player1 = PlayerSerializer()
    player2 = PlayerSerializer()
    ball_coordinates = BallCoordinatesSerializer()

    class Meta:
        model = Game
        fields = ['id', 'player1', 'player2', 'created_at', 'ball_coordinates']
