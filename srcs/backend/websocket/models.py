from django.db import models
from CustomUser.models import CustomUser

# Create your models here.
class MatchmakingQueue(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    websocket_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class MatchmakingRoom(models.Model):
    player1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="player1")
    player2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="player2")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.id}"

    