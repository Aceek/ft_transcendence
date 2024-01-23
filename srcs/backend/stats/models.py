from django.db import models
from CustomUser.models import CustomUser

# Create Models stats link to CustomUser

class Stats(models.Model):
    user = models.OneToOneField(to="CustomUser.CustomUser", on_delete=models.CASCADE)
    win = models.IntegerField(default=0)
    lose = models.IntegerField(default=0)
    elo = models.IntegerField(default=1000)
    win_streak = models.IntegerField(default=0)
    lose_streak = models.IntegerField(default=0)
    biggest_win_streak = models.IntegerField(default=0)


class MatchHistory(models.Model):
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user2")
    winner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="winner")
    date = models.DateTimeField(auto_now_add=True)