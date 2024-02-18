from CustomUser.models import CustomUser
from stats.models import MatchHistory, EloHistory


class manageStats:
    def __init__(self, user1: CustomUser, user2: CustomUser, winner: CustomUser):
        """_summary_
        Initialise un objet pour gérer les statistiques des utilisateurs.
        Args:
            user1 (CustomUser): user1 of the match.
            user2 (CustomUser): user2 of the match.
            winner (CustomUser): winner of the match must be user1 or user2.
        """
        self.user1 = user1
        self.user2 = user2
        self.winner = winner
        if winner not in [user1, user2]:
            raise ValueError("winner must be user1 or user2")
        self.looser = user1 if winner == user2 else user2

    def recordMatch(self):
        """_summary_
        Enregistre un match dans la base de données.
        Le paramètre 'winner' doit être soit 'user1' soit 'user2'.

        Raises:
            ValueError: _description_
        """
        match = MatchHistory(user1=self.user1, user2=self.user2, winner=self.winner)
        match.save()
        self.addWin(self.winner)
        self.addLose(self.user1 if self.winner == self.user2 else self.user2)
        self.calculateElo(
            self.winner, self.user1 if self.winner == self.user2 else self.user2
        )

    def createNewEloHistory(user: CustomUser, newElo: int):
        """_summary_
        Crée un nouvel enregistrement d'historique Elo pour un utilisateur.
        Args:
            user (CustomUser): The user to update the Elo.
            newElo (int): Elo after the match.

        Raises:
            TypeError: _description_
        """
        if not isinstance(user, CustomUser):
            raise TypeError("user must be an instance of CustomUser")
        elo = EloHistory(user=user, elo=newElo)
        elo.save()

    def addWin(self):
        """_summary_
        Ajoute une victoire à l'utilisateur.

        Raises:
            TypeError: user must be an instance of CustomUser
        """
        self.winner.stats.win += 1
        self.winner.stats.win_streak += 1
        if self.winner.stats.win_streak > self.winner.stats.biggest_win_streak:
            self.winner.stats.biggest_win_streak = self.winner.stats.win_streak
        self.winner.stats.save()

    def addLose(self):
        """
        add a lose to the user.
        """
        self.looser.stats.lose += 1
        self.looser.stats.lose_streak += 1
        self.looser.stats.win_streak = 0
        self.looser.stats.save()

    def calculateElo(self, k=64):
        """_summary_
        Calcule le score Elo pour chaque joueur et met à jour la base de données.
        Args:
            k (int, optional): indice power of win/loose elo. Defaults to 64.
        """
        # Calculez l'espérance de gain pour chaque joueur
        expected_winner = 1 / (
            1 + 10 ** ((self.loser.stats.elo - self.winner.stats.elo) / 400)
        )
        expected_loser = 1 / (
            1 + 10 ** ((self.winner.stats.elo - self.loser.stats.elo) / 400)
        )

        # Mettez à jour le score Elo du gagnant
        self.winner.stats.elo = self.winner.stats.elo + k * (1 - expected_winner)
        self.createNewEloHistory(self.winner, self.winner.stats.elo)

        # Mettez à jour le score Elo du perdant
        self.loser.stats.elo = self.loser.stats.elo + k * (0 - expected_loser)
        if self.loser.stats.elo < 0:
            self.loser.stats.elo = 0
        self.createNewEloHistory(self.loser, self.loser.stats.elo)

        # Enregistrez les modifications
        self.winner.stats.save()
        self.loser.stats.save()
