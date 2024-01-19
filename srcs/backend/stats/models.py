from django.db import models

# Create Models stats link to CustomUser

class Stats(models.Model):
    user = models.ForeignKey(to="CustomUser.CustomUser", on_delete=models.CASCADE)
    win = models.IntegerField(default=0)
    lose = models.IntegerField(default=0)
    elo = models.IntegerField(default=1000)
    win_streak = models.IntegerField(default=0)
    lose_streak = models.IntegerField(default=0)
    biggest_win_streak = models.IntegerField(default=0)
