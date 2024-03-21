from .models import LocalMatches, LocalTournament
import random


class ManageLocalTournament:
    def __init__(self, tournament: LocalTournament):
        self.tournament = tournament
        # all the aliases in the tournament as a list
        self.aliases = tournament.participants

    def organize_matches(self):
        # randomize the aliases list
        random.shuffle(self.aliases)
        if len(self.aliases) % 2 != 0:
            # if the number of aliases is odd, we remove the last one and treat as bye
            byeAlias = self.aliases.pop()
            # Handle bye match case here, if necessary

        # create matches
        for i in range(0, len(self.aliases), 2):
            alias1 = self.aliases[i]
            alias2 = self.aliases[i + 1]
            match = LocalMatches.objects.create(
                tournament=self.tournament,
                player1=alias1,
                player2=alias2,
                is_active=True,
                round=self.tournament.round,
            )
            # Note: Adjust room_url or remove if not needed
            match.save()

    def end_round(self):
        matches = LocalMatches.objects.filter(
            tournament=self.tournament, round=self.tournament.round
        )
        winners = [match.winner for match in matches if match.winner]
        # if there is only one winner, the tournament is finished
        if len(winners) == 1:
            self.tournament.is_finished = True
            self.tournament.is_active = False
            self.tournament.winner = winners[0]
            self.tournament.save()
            # Handle tournament end notification, if necessary
            return
        self.tournament.round += 1
        self.tournament.save()
        # Prepare the next round with winners
        self.aliases = winners
        self.organize_matches()

    def verify_round_end(self):
        matches = LocalMatches.objects.filter(
            tournament=self.tournament, round=self.tournament.round
        )
        if all(match.is_finished for match in matches):
            self.end_round()

    def set_end_match(self, match: LocalMatches, winner_alias: str, verify=True):
        match.is_active = False
        match.is_finished = True
        match.winner = winner_alias
        match.save()
        if verify:
            self.verify_round_end()
