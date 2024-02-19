from django.db import models
import uuid


# Create your models here.
class Tournament(models.Model):
    ownerUser = models.ForeignKey(
        "CustomUser.CustomUser",
        on_delete=models.CASCADE,
        related_name="ownerUser",
        null=True,
    )
    winner = models.ForeignKey(
        "CustomUser.CustomUser",
        on_delete=models.CASCADE,
        related_name="winnerofTournament",
        null=True,
        editable=False,
    )
    round = models.IntegerField(default=1, editable=False)
    place_left = models.IntegerField(default=8, editable=False)
    name = models.CharField(max_length=20)
    max_participants = models.IntegerField()
    is_active = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ManyToManyField(
        "CustomUser.CustomUser", related_name="tournament", blank=True
    )
    # uid as primary key
    uid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )


class Matches(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="matches"
    )
    user1 = models.ForeignKey(
        "CustomUser.CustomUser",
        on_delete=models.CASCADE,
        related_name="user1ofMatch",
        null=True,
    )
    user2 = models.ForeignKey(
        "CustomUser.CustomUser",
        on_delete=models.CASCADE,
        related_name="user2ofMatch",
        null=True,
    )
    winner = models.ForeignKey(
        "CustomUser.CustomUser",
        on_delete=models.CASCADE,
        related_name="winnerofMatch",
        null=True,
    )
    round = models.IntegerField(default=1, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)
    is_draw = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    uid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
