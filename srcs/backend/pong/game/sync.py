import asyncio
import time

from .enum import GameStatus
from .config import READY_TIMER, FORFEIT_TIMER, EXIT_GAME_LOGIC_TIMER

class GameSync:
    def __init__(self, game):
        self.redis_ops = game.redis_ops
        self.room_name = game.room_name
        self.player_nb = game.player_nb if game.mode == "online" else 1
        self.game_type = game.type
        self.channel_com = game.channel_com

    async def countdown(self, duration=READY_TIMER):
        print(f"Countdown starting for {duration} seconds.")
        for i in range(duration, 0, -1):
            await self.channel_com.send_countdown(i)
            print(f"Countdown: {i}")
            await asyncio.sleep(1)
        await self.channel_com.send_countdown(0)
        print("Countdown finished.")

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

    async def wait_for_players_to_start(self, current_status):
        if self.game_type == "tournament":
            if current_status == GameStatus.SUSPENDED:
                return await self.wait_for_tournament_to_resume()
            elif current_status == GameStatus.UNSTARTED:
                return not await self.wait_for_tournament_to_exit(current_status)

        return await self.wait_for_players(
            self.check_for_players_ready,
            "Checking if players are ready"
        )

    async def wait_for_players_to_restart(self):
        if await self.wait_for_players(
            self.check_for_restart_conditions, 
            "Checking if players are ready to restart"
        ):
            print("Players are ready. Game can restart.")
            return True
        return False

    async def wait_for_tournament_to_exit(self, current_status):
        start_time = time.time()
        last_connected_time = start_time

        while True:
            connected_users_count = await self.redis_ops.get_connected_users_nb()

            if current_status != GameStatus.COMPLETED and \
                connected_users_count == self.player_nb:
                print("All players connected. Tournament game can start.")
                return False
            elif connected_users_count > 0:
                last_connected_time = time.time()
            
            if time.time() - last_connected_time > EXIT_GAME_LOGIC_TIMER:
                print("No connected users anymore, game loop can exit.")
                return True

            await asyncio.sleep(1)

    async def wait_for_tournament_to_resume(self):
        start_time = time.time()
        duration = FORFEIT_TIMER

        while time.time() - start_time < duration:
            connected_users_count = await self.redis_ops.get_connected_users_nb()
            if connected_users_count == self.player_nb:
                print("All players connected. Tournament game can resume.")
                return True
            
            # Send countdown to frontend
            remaining_time = int(duration - (time.time() - start_time))
            await self.channel_com.send_countdown(remaining_time)
            
            await asyncio.sleep(1)

        print("Not all players were ready for the tournament to resume.")
        await self.channel_com.send_countdown(0)
        return False

    async def check_for_players_ready(self):
        connected_users_count = await self.redis_ops.get_connected_users_nb()
        if connected_users_count == self.player_nb:
            return True, "All players connected."
        elif connected_users_count == 0:
            return False, "No player in the room anymore."
        return None, "Waiting for players to start the game..."

    async def check_for_restart_conditions(self):
        connected_users_count = await self.redis_ops.get_connected_users_nb()
        restart_requests_count = await self.redis_ops.get_restart_requests()
        if restart_requests_count == connected_users_count == self.player_nb:
            return True, "All players connected, game can restart."
        elif connected_users_count == 0:
            return False, "No player in the room anymore to restart the game."
        return None, "Waiting for players to restart the game..."
    