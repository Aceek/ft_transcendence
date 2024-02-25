import asyncio

from .game_status import *

class GameSync:
    def __init__(self, redis, room_name):
        self.redis = redis
        self.room_name = room_name

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

    async def check_for_initial_players(self):
        connected_users_count = await self.redis.scard(f"game:{self.room_name}:connected_users")
        if connected_users_count >= 2:
            return True, "Both players connected."
        elif connected_users_count == 0:
            return False, "No player in the room anymore."
        return None, "Waiting for players to start the game..."

    # async def check_for_restart_conditions(redis, room_name):
    #     """Check condition for game restart waiting."""
    #     connected_users_count = await redis.scard(f"game:{room_name}:connected_users")
    #     restart_requests_count = await redis.scard(f"game:{room_name}:restart_requests")
    #     if restart_requests_count == connected_users_count == 2:
    #         await redis.delete(f"game:{room_name}:restart_requests")
    #         return True, "All players in room are ready to restart the game."
    #     elif connected_users_count == 0:
    #         return False, "All players in room have left."
    #     return None, "Waiting for players to restart the game..."

    async def wait_for_players_to_start(self):
        """Check if players are ready to start the game."""
        # Call the wait_for_players method correctly using self and passing the condition_check method also through self
        if await self.wait_for_players(
            self.check_for_initial_players,
            "Checking if players are ready"
        ):
            print("Players are ready. Game can start.")
            return True
        return False


    # async def wait_for_players_to_resume(redis, room_name):
    #     """Wait for other players to reconnect or join for the game to resume."""
    #     await update_and_send_redis_game_status(GameStatus.WAITING_PLAYERS)
    #     game_resume = await wait_for_players(
    #         check_for_initial_players, 
    #         "Waiting for other players to resume"
    #     )
    #     if game_resume:
    #         print("Players are ready. Game can resume.")
    #         await send_redis_data_to_channel()
    #         await update_and_send_redis_game_status(GameStatus.IN_PROGRESS)
    #         return True
    #     return False

    # async def wait_for_players_to_restart(redis, room_name):
    #     """Wait for other players to restart the game."""
    #     game_restart = await wait_for_players(
    #         check_for_restart_conditions, 
    #         "Checking if players are ready to restart"
    #     )
    #     if game_restart:
    #         print("Players are ready. Game can restart.")
    #         await run()
    #         return True
    #     # await clear_redis_room_data(room_name)
    #     return False