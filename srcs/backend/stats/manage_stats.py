from CustomUser.models import CustomUser
from stats.models import MatchHistory


def record_match(user1, user2, winner):
    """
    Enregistre un match dans la base de données.
    Le paramètre 'winner' doit être soit 'user1' soit 'user2'.
    """
    if not isinstance(user1, CustomUser) or not isinstance(user2, CustomUser):
        raise TypeError("user must be an instance of CustomUser")
    if winner not in [user1, user2]:
        raise ValueError("winner must be user1 or user2")

    match = MatchHistory(user1=user1, user2=user2, winner=winner)
    match.save()
    add_win(winner)
    add_lose(user1 if winner == user2 else user2)
    calculate_elo(winner, user1 if winner == user2 else user2)


def add_win(user):
    """
    Ajoute une victoire à l'utilisateur.
    """
    if not isinstance(user, CustomUser):
        raise TypeError("user must be an instance of CustomUser")
    user.stats.win += 1
    user.stats.win_streak += 1
    if user.stats.win_streak > user.stats.biggest_win_streak:
        user.stats.biggest_win_streak = user.stats.win_streak
    user.stats.save()


def add_lose(user):
    """
    Ajoute une défaite à l'utilisateur.
    """
    if not isinstance(user, CustomUser):
        raise TypeError("user must be an instance of CustomUser")
    user.stats.lose += 1
    user.stats.lose_streak += 1
    user.stats.win_streak = 0
    user.stats.save()


def calculate_elo(winner, loser, k=32):
    """
    Calcule le nouveau score Elo pour le gagnant et le perdant.
    Le paramètre 'k' est le facteur de pondération du match.
    """
    if not isinstance(winner, CustomUser) or not isinstance(loser, CustomUser):
        raise TypeError("user must be an instance of CustomUser")
    # Calculez l'espérance de gain pour chaque joueur
    expected_winner = 1 / (1 + 10 ** ((loser.stats.elo - winner.stats.elo) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner.stats.elo - loser.stats.elo) / 400))

    # Mettez à jour le score Elo du gagnant
    winner.stats.elo = winner.stats.elo + k * (1 - expected_winner)

    # Mettez à jour le score Elo du perdant
    loser.stats.elo = loser.stats.elo + k * (0 - expected_loser)
    if winner.stats.elo < 0:
        winner.stats.elo = 0

    # Enregistrez les modifications
    winner.stats.save()
    loser.stats.save()
