import asyncio

class GameSync:
    def __init__(self, redis_ops, room_name, player_nb):
        self.redis_ops = redis_ops
        self.room_name = room_name
        self.player_nb = player_nb

    async def wait_for_players(self, condition_check, status_message):
        print(f"{status_message} in room: {self.room_name}")
        while True:
            condition_met, message = await condition_check()
            if condition_met:
                print(message)
                return True
            elif condition_met is False:
                print(message)
                return False
            await asyncio.sleep(1)

    async def wait_for_players_to_start(self):
        """Check if players are ready to start the game."""
        if await self.wait_for_players(
            self.check_for_players_ready,
            "Checking if players are ready"
        ):
            print("Players are ready. Game can start.")
            return True
        return False

    async def wait_for_players_to_restart(self):
        """Wait for other players to restart the game."""
        if await self.wait_for_players(
            self.check_for_restart_conditions, 
            "Checking if players are ready to restart"
        ):
            print("Players are ready. Game can restart.")
            return True
        return False

    async def check_for_players_ready(self):
        connected_users_count = await self.redis_ops.get_connected_users()
        if connected_users_count == self.player_nb:
            return True, "Both players connected."
        elif connected_users_count == 0:
            return False, "No player in the room anymore."
        return None, "Waiting for players to start the game..."

    async def check_for_restart_conditions(self):
        """Check condition for game restart waiting."""
        connected_users_count = await self.redis_ops.get_connected_users()
        restart_requests_count = await self.redis_ops.get_restart_requests()
        if restart_requests_count == connected_users_count == self.player_nb:
            return True, "All players in room are ready to restart the game."
        elif connected_users_count == 0:
            return False, "All players in room have left."
        return None, "Waiting for players to restart the game..."
    