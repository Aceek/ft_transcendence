from django.db import models
from CustomUser.models import CustomUser


# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="received_messages"
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)


class TournamentNotifications(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="tournament_notifications"
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
