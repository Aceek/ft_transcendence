# pong/serializers.py
from rest_framework import serializers
from .models import *

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['player_id', 'score']

class PaddleCoordinatesSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()

    class Meta:
        model = PaddleCoordinates
        fields = ['player', 'paddle_y']

class BallCoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BallCoordinates
        fields = ['x_position', 'y_position']

class GameSerializer(serializers.ModelSerializer):
    player1 = PlayerSerializer()
    player2 = PlayerSerializer()
    paddle_coordinates = PaddleCoordinatesSerializer(many=True)
    ball_coordinates = BallCoordinatesSerializer()

    class Meta:
        model = Game
        fields = ['id', 'player1', 'player2', 'created_at', 'paddle_coordinates', 'ball_coordinates']
