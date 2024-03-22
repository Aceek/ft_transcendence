from .models import Tournament, Matches, LocalMatches, LocalTournament
import random
from CustomUser.models import CustomUser
from stats.manage_stats import ManageHistory
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class ManageTournament:
    def __init__(self, tournament):
        self.tournament = tournament
        self.is_local = isinstance(tournament, LocalTournament)
        if self.is_local:
            self.users = tournament.participants
            self.MatchModel = LocalMatches
        else:
            self.users = list(tournament.user.all())
            self.MatchModel = Matches

    def organize_matches(self):
        # randomize the users list
        random.shuffle(self.users)
        if len(self.users) % 2 != 0:
            # if the number of users is odd, we remove the last one
            byeUser = self.users.pop()
            byeMatch = self.MatchModel.objects.create(
                tournament=self.tournament,
                user1=byeUser,
                user2=byeUser,
                is_active=True,
                is_finished=True,
                round=self.tournament.round,
            )
            byeMatch.room_url = ""
            self.set_end_match(byeMatch, byeUser, False)
            byeMatch.save()
        # create matches
        for i in range(0, len(self.users), 2):
            user1 = self.users[i]
            user2 = self.users[i + 1]
            match = self.MatchModel.objects.create(
                tournament=self.tournament,
                user1=user1,
                user2=user2,
                is_active=True,
                round=self.tournament.round,
            )
            if self.is_local:
                match.room_url = f"/pong/offline/2/tournament/{str(match.uid)}"
            else:
                match.room_url = f"/pong/online/2/tournament/{str(match.uid)}"
            match.save()
            if not self.is_local:
                self.send_messages_join_match_users(match)
                self.notify_match_ready(match)
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
            if not self.is_local:
                self.notify_tournament_end()
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

    def set_end_match(self, match, winner, verify=True):
        match.is_active = False
        match.is_finished = True
        match.winner = winner
        if not self.is_local:
            match.is_in_game = False
        match.save()
        if not self.is_local:
            ManageHistory(user1=match.user1, user2=match.user2, winner=winner)
            self.notify_match_end(match)
        if verify:
            self.verify_round_end()

    def get_nb_users(self):
        return len(self.users)

    def get_matches(self):
        return self.MatchModel.objects.filter(tournament=self.tournament)

    def get_matches_by_round(self, round):
        return self.MatchModel.objects.filter(tournament=self.tournament, round=round)

    def get_tournament(self):
        return self.tournament

    def get_users(self):
        return self.users

    def notify_tournament_group(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"tournament_{str(self.tournament.uid)}",
            {
                "type": "tournament_message",
                "action": "tournament_active",
                "message": f"Tournament {str(self.tournament.uid)} is active",
                "tournamentId": str(self.tournament.uid),
            },
        )

    def send_messages_join_tournaments_users(self):
        for user in self.users:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{user.id}",
                {
                    "action": "join_tournament",
                    "type": "send_tournament",
                    "tournamentId": str(self.tournament.uid),
                },
            )

    def send_messages_join_match_users(self, match: Matches):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{match.user1.id}",
            {
                "type": "send_match",
                "message": f"Match {str(match.uid)} is ready",
                "action": "join_match",
                "tournamentId": str(self.tournament.uid),
                "matchId": str(match.uid),
            },
        )
        async_to_sync(channel_layer.group_send)(
            f"chat_{match.user2.id}",
            {
                "type": "send_match",
                "message": f"Match {str(match.uid)} is ready",
                "action": "join_match",
                "tournamentId": str(self.tournament.uid),
                "matchId": str(match.uid),
            },
        )

    def notify_match_ready(self, match: Matches):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"match_{str(match.uid)}",
            {
                "type": "send_match",
                "action": "match_ready",
                "tournamentId": str(self.tournament.uid),
                "message": f"Match {str(match.uid)} is ready for tournament {str(self.tournament.uid)}",
                "matchId": str(match.uid),
            },
        )

    def notify_match_end(self, match: Matches):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"match_{str(match.uid)}",
            {
                "type": "send_match",
                "action": "match_end",
                "tournamentId": str(self.tournament.uid),
                "message": f"Match {str(match.uid)} is ended for tournament {str(self.tournament.uid)}",
                "matchId": str(match.uid),
            },
        )

    def notify_tournament_end(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"tournament_{str(self.tournament.uid)}",
            {
                "type": "tournament_message",
                "action": "tournament_end",
                "message": f"Tournament {str(self.tournament.uid)} is ended",
                "tournamentId": str(self.tournament.uid),
            },
        )
