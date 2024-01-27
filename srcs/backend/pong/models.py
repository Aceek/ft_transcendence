from django.db import models

class Game(models.Model):
    player1_id = models.CharField(max_length=50)
    player2_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game {self.id}"

class PaddleCoordinates(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player_id = models.CharField(max_length=50)
    paddle_y = models.IntegerField()
    direction = models.CharField(max_length=10)  # Add direction field

    def __str__(self):
        return f"PaddleCoordinates for Game {self.game_id}, Player {self.player_id}"
