# models.py
from django.db import models
from .game_config import *

class Player(models.Model):
    player_id = models.CharField(max_length=50, unique=True)
    score = models.IntegerField(default=INITIAL_SCORE)
    paddle_y = models.IntegerField(default=INITIAL_PADDLE_Y)

    def __str__(self):
        return f"Player {self.player_id}"

class Game(models.Model):
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player1_games', default=1)
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player2_games', default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    ball = models.OneToOneField('BallCoordinates', on_delete=models.CASCADE, null=True, blank=True, related_name='game_ball')
    ongoing = models.BooleanField(default=False)

    def __str__(self):
        return f"Game between {self.player1} and {self.player2}, Match Ongoing: {self.match_ongoing}"


class BallCoordinates(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='ball_coordinates')
    x = models.IntegerField(default=INITIAL_BALL_X)
    y = models.IntegerField(default=INITIAL_BALL_Y)
    speed_x = models.FloatField(default=0)
    speed_y = models.FloatField(default=0)

    def __str__(self):
        return f"BallCoordinates for Game {self.game.id}"
