from CustomUser.models import CustomUser
from stats.models import MatchHistory, EloHistory


class manageStats:
    def __init__(self, user1: CustomUser, user2: CustomUser, winner: CustomUser):
        self.user1 = user1
        self.user2 = user2
        self.winner = winner
        self.looser = user1 if winner == user2 else user2

    def recordMatch(self):
        """_summary_
        Enregistre un match dans la base de données.
        Le paramètre 'winner' doit être soit 'user1' soit 'user2'.

        Raises:
            ValueError: _description_
        """
        if self.winner not in [self.user1, self.user2]:
            raise ValueError("winner must be user1 or user2")
        match = MatchHistory(user1=self.user1, user2=self.user2, winner=self.winner)
        match.save()
        self.addWin(self.winner)
        self.addLose(self.user1 if self.winner == self.user2 else self.user2)
        self.calculateElo(
            self.winner, self.user1 if self.winner == self.user2 else self.user2
        )

    def createNewEloHistory(user, newElo):
        """_summary_
        Args:
            user (_type_): _description_
            newElo (_type_): _description_

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
        if not isinstance(self.winner, CustomUser):
            raise TypeError("user must be an instance of CustomUser")
        self.winner.stats.win += 1
        self.winner.stats.win_streak += 1
        if self.winner.stats.win_streak > self.winner.stats.biggest_win_streak:
            self.winner.stats.biggest_win_streak = self.winner.stats.win_streak
        self.winner.stats.save()

    def addLose(self):
        """
        Ajoute une défaite à l'utilisateur.
        """
        if not isinstance(self.looser, CustomUser):
            raise TypeError("user must be an instance of CustomUser")
        self.looser.stats.lose += 1
        self.looser.stats.lose_streak += 1
        self.looser.stats.win_streak = 0
        self.looser.stats.save()

    def calculateElo(self, k=64):
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
        createNewEloHistory(winner, winner.stats.elo)

        # Mettez à jour le score Elo du perdant
        loser.stats.elo = loser.stats.elo + k * (0 - expected_loser)
        if loser.stats.elo < 0:
            loser.stats.elo = 0
        createNewEloHistory(loser, loser.stats.elo)

        # Enregistrez les modifications
        winner.stats.save()
        loser.stats.save()
