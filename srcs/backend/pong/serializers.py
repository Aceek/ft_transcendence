# pong/serializers.py
# from rest_framework import serializers
# from .game_config import *
# from .models import *

# class PlayerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Player
#         fields = ['player_id', 'score', 'paddle_y']

# class BallCoordinatesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BallCoordinates
#         fields = ['x', 'y', 'speed_x', 'speed_y']

# class GameSerializer(serializers.ModelSerializer):
#     player1 = PlayerSerializer()
#     player2 = PlayerSerializer()
#     ball_coordinates = BallCoordinatesSerializer()

#     # # Additional fields not present in the Game model
#     # screen = serializers.SerializerMethodField()
#     # paddle = serializers.SerializerMethodField()
#     # ball = serializers.SerializerMethodField()
#     # players = serializers.SerializerMethodField()

#     class Meta:
#         model = Game
#         fields = ['id', 'player1', 'player2', 'created_at', 'ongoing', 'ball_coordinates']
#         # fields = ['id', 'player1', 'player2', 'created_at', 'ongoing', 'ball_coordinates', 'screen', 'paddle', 'ball', 'players']

#     # def get_screen(self, obj):
#     #     return {'width': SCREEN_WIDTH, 'height': SCREEN_HEIGHT}

#     # def get_paddle(self, obj):
#     #     return {'width': PADDLE_WIDTH, 'height': PADDLE_HEIGHT, 'speed': PADDLE_SPEED}

#     # def get_ball(self, obj):
#     #     return {'width': BALL_WIDTH, 'height': BALL_HEIGHT, 'speed_x': obj.ball_coordinates.speed_x, 'speed_y': obj.ball_coordinates.speed_y, 'x': obj.ball_coordinates.x, 'y': obj.ball_coordinates.y}

#     # def get_players(self, obj):
#     #     return [
#     #         {'player_id': obj.player1.player_id, 'score': obj.player1.score, 'paddle_y': obj.player1.paddle_y},
#     #         {'player_id': obj.player2.player_id, 'score': obj.player2.score, 'paddle_y': obj.player2.paddle_y}
#     #     ]
