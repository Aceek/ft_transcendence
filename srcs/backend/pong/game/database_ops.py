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


    # @database_sync_to_async
    # def get_match(self, match_id):
    #     """Asynchronously retrieves a Match object based on match ID."""
    #     try:
    #         return Match.objects.get(pk=match_id)
    #     except Match.DoesNotExist:
    #         return None

    # @database_sync_to_async
    # def get_tournament(self, tournament_id):
    #     """Asynchronously retrieves a Tournament object based on tournament ID."""
    #     try:
    #         return Tournament.objects.get(pk=tournament_id)
    #     except Tournament.DoesNotExist:
    #         return None
