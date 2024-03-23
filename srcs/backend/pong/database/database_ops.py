from channels.db import database_sync_to_async
from django.db import IntegrityError

class DatabaseOps:
    @database_sync_to_async
    def get_custom_user(self, user_id):
        from CustomUser.models import CustomUser

        try:
            user = CustomUser.objects.get(pk=user_id)
            return user
        
        except CustomUser.DoesNotExist:
            print(f"User with ID {user_id} does not exist.")
            return None

    @database_sync_to_async
    def get_match_and_tournament(self, match_id):
        from tournament.models import Matches

        try:
            match = Matches.objects.get(pk=match_id)
            tournament = match.tournament
            return match, tournament

        except Matches.DoesNotExist:
            print(f"Match with ID {match_id} does not exist.")
            return None, None

    @database_sync_to_async
    def get_local_match_and_tournament(self, match_id):
        from tournament.models import LocalMatches

        try:
            match = LocalMatches.objects.get(pk=match_id)
            tournament = match.tournament
            return match, tournament

        except LocalMatches.DoesNotExist:
            print(f"Match with ID {match_id} does not exist.")
            return None, None

    @database_sync_to_async
    def set_user_status(self, user_id, status):
        from CustomUser.models import CustomUser

        try:
            user = CustomUser.objects.get(pk=user_id)
            user.status = status
            user.save(update_fields=['status'])
            return True
        except CustomUser.DoesNotExist:
            print(f"User with ID {user_id} does not exist.")
            return False
        except IntegrityError as e:
            print(f"Error updating status for user {user_id}: {e}")
            return False

    @database_sync_to_async
    def update_match_history(self, winner, players):
        from stats.manage_stats import ManageHistory

        self.history_manager = ManageHistory(players[0].user, players[1].user, winner.user)

    @database_sync_to_async
    def update_tournament(self, mode, match, tournament, winner):
        from tournament.manageTournament import ManageTournament

        winner_field = winner.user if mode == "online" else winner.username

        self.tournament_manager = ManageTournament(tournament)
        self.tournament_manager.set_end_match(match, winner_field)
