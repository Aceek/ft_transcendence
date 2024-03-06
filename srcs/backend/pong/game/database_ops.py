from channels.db import database_sync_to_async
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
    def update_match_history(self, winner, players):
        from stats.manage_stats import ManageHistory

        self.manage_history = ManageHistory(players[0].user, players[1].user, winner.user)

