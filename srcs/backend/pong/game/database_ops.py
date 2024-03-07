from channels.db import database_sync_to_async

class DatabaseOps:
    @database_sync_to_async
    def get_custom_user(self, user_id):
        from CustomUser.models import CustomUser

        """Asynchronously retrieves a CustomUser object based on user ID."""
        try:
            user = CustomUser.objects.get(pk=user_id)
            print(f"Successfully retrieved user: {user.username} (ID: {user_id})")
            return user
        except CustomUser.DoesNotExist:
            print(f"User with ID {user_id} does not exist.")
            return None

    @database_sync_to_async
    def get_match(self, match_id):
        from tournament.models import Matches

        """Asynchronously retrieves a Match object based on user ID."""
        try:
            match = Matches.objects.get(pk=match_id)
            print(f"Successfully retrieved match: {match.uid}")
            return match
        except Matches.DoesNotExist:
            print(f"Match with ID {match_id} does not exist.")
            return None

    @database_sync_to_async
    def get_tournament(self, tournament_id):
        from tournament.models import Tournament

        """Asynchronously retrieves a Match object based on user ID."""
        try:
            tournament = Tournament.objects.get(pk=tournament_id)
            print(f"Successfully retrieved match: {tournament.name}")
            return tournament
        except Tournament.DoesNotExist:
            print(f"Match with ID {tournament_id} does not exist.")
            return None


    @database_sync_to_async
    def update_match_history(self, winner, players):
        from stats.manage_stats import ManageHistory

        self.history_manager = ManageHistory(players[0].user, players[1].user, winner.user)

    @database_sync_to_async
    def update_tournament(self, tournament, match, winner):
        from tournament.manageTournament import ManageTournament

        self.tournament_manager = ManageTournament(tournament)
        self.tournament_manager.set_end_match(match, winner)