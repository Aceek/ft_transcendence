from .models import Tournament, Matches
import random
from CustomUser.models import CustomUser
from stats.manage_stats import ManageHistory


class ManageTournament:
    def __init__(self, tournament: Tournament):
        self.tournament = tournament
        # all the users in the tournament as a list
        self.users = list(tournament.user.all())

    def organize_matches(self):
        # randomize the users list
        random.shuffle(self.users)
        if len(self.users) % 2 != 0:
            # if the number of users is odd, we remove the last one
            byeUser = self.users.pop()
            byeMatch = Matches.objects.create(
                tournament=self.tournament,
                user1=byeUser,
                user2=byeUser,
                is_active=True,
                is_finished=True,
                round=self.tournament.round,
            )
            self.set_end_match(byeMatch, byeUser, False)
            byeMatch.save()
        # create matches
        for i in range(0, len(self.users), 2):
            user1 = self.users[i]
            user2 = self.users[i + 1]
            match = Matches.objects.create(
                tournament=self.tournament,
                user1=user1,
                user2=user2,
                is_active=True,
                round=self.tournament.round,
            )
            match.save()
            print("match created : ", match, " round : ", self.tournament.round)
        self.tournament.save()

    def end_round(self):
        matches = self.get_matches_by_round(self.tournament.round)
        winners = [match.winner for match in matches]
        # if there is only one winner, the tournament is finished
        if len(winners) == 1:
            self.tournament.is_finished = True
            self.tournament.is_active = False
            self.tournament.winner = winners[0]
            self.tournament.save()
            return
        self.tournament.round += 1
        self.tournament.save()
        # if there is more than one winner, we start a new round
        self.users = winners
        self.organize_matches()

    def verify_round_end(self):
        matches = self.get_matches_by_round(self.tournament.round)
        if all([match.is_finished for match in matches]):
            self.end_round()
            print("round ended")
        else:
            print("round not ended")

    def set_end_match(self, match: Matches, winner: CustomUser, verify=True):
        match.is_active = False
        match.is_finished = True
        match.is_in_game = False
        match.winner = winner
        ManageHistory(user1=match.user1, user2=match.user2, winner=winner)
        match.save()
        if verify:
            self.verify_round_end()

    def get_nb_users(self):
        return len(self.users)

    def get_matches(self):
        return Matches.objects.filter(tournament=self.tournament)

    def get_matches_by_round(self, round):
        return Matches.objects.filter(tournament=self.tournament, round=round)

    def get_tournament(self):
        return self.tournament

    def get_users(self):
        return self.users
