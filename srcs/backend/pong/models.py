from django.db import models
from .game_config import INITIAL_PADDLE_Y, INITIAL_BALL_X, INITIAL_BALL_Y

class Player(models.Model):
    player_id = models.CharField(max_length=50, unique=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"Player {self.player_id}"

class Game(models.Model):
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player1_games', default=1)
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player2_games', default=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game {self.id}"

class PaddleCoordinates(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, default=1)
    paddle_y = models.IntegerField(default=INITIAL_PADDLE_Y)

    def __str__(self):
        return f"PaddleCoordinates for Game {self.game.id}, Player {self.player.player_id}"

class BallCoordinates(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    x_position = models.IntegerField(default=INITIAL_BALL_X)
    y_position = models.IntegerField(default=INITIAL_BALL_Y)

    def __str__(self):
        return f"BallCoordinates for Game {self.game.id}"
