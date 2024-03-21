from django.db import models
import uuid
from django.contrib.postgres.fields import ArrayField


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
    is_in_game = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    uid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    room_url = models.CharField(max_length=100, null=True, blank=True, editable=False)


class LocalTournament(models.Model):
    localOwnerUser = models.ForeignKey(
        "CustomUser.CustomUser",
        on_delete=models.CASCADE,
        related_name="owned_local_tournaments",
        null=True,
    )
    winner = models.CharField(max_length=100, null=True, blank=True, editable=False)
    round = models.IntegerField(default=1, editable=False)
    name = models.CharField(max_length=20)
    max_participants = models.IntegerField()
    is_active = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    participants = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name

class LocalMatch(models.Model):
    tournament = models.ForeignKey(LocalTournament, on_delete=models.CASCADE, related_name="local_matches")
    player1 = models.CharField(max_length=100)
    player2 = models.CharField(max_length=100)
    winner = models.CharField(max_length=100, null=True, blank=True)
    round = models.IntegerField(default=1, editable=False)
    is_finished = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    room_url = models.CharField(max_length=100, null=True, blank=True, editable=False)  # Optionnel, selon l'usage hors ligne

    def __str__(self):
        return f"Match {self.uid} in Tournament {self.tournament.name}"