from django.db import models

class PaddleCoordinates(models.Model):
    game_id = models.PositiveIntegerField(unique=True)
    paddle_left_y = models.FloatField()
    paddle_right_y = models.FloatField()

    def __str__(self):
        return f"Paddle Coordinates - Game {self.game_id}"
