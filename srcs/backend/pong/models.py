# models.py
from django.db import models
from .game_config import INITIAL_PADDLE_Y, INITIAL_BALL_X, INITIAL_BALL_Y

class Player(models.Model):
    player_id = models.CharField(max_length=50, unique=True)
    score = models.IntegerField(default=0)
    paddle_y = models.IntegerField(default=INITIAL_PADDLE_Y)

    def __str__(self):
        return f"Player {self.player_id}"

class Game(models.Model):
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player1_games', default=1)
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player2_games', default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    ball = models.OneToOneField('BallCoordinates', on_delete=models.CASCADE, null=True, blank=True, related_name='game_ball')

    def __str__(self):
        return f"Game {self.id}"

class BallCoordinates(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='ball_coordinates')
    x = models.IntegerField(default=INITIAL_BALL_X)
    y = models.IntegerField(default=INITIAL_BALL_Y)

    def __str__(self):
        return f"BallCoordinates for Game {self.game.id}"
