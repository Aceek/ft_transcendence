import asyncio
import time

from .enum import GameStatus

class GameSync:
    def __init__(self, game):
        self.redis_ops = game.redis_ops
        self.room_name = game.room_name
        self.player_nb = game.player_nb
        self.game_type = game.type
        self.channel_com = game.channel_com

    async def countdown(self, duration=3):
        """Handles the countdown logic."""
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
        """Check if players are ready to start the game."""
        # Special handling for tournament games
        if self.game_type == "tournament" and current_status == GameStatus.SUSPENDED:
            return await self.wait_for_tournament_to_resume()
        
        # Default handling for non-tournament games
        return await self.wait_for_players(
            self.check_for_players_ready,
            "Checking if players are ready"
        )

    async def wait_for_players_to_restart(self):
        """Wait for other players to restart the game."""
        if await self.wait_for_players(
            self.check_for_restart_conditions, 
            "Checking if players are ready to restart"
        ):
            print("Players are ready. Game can restart.")
            return True
        return False
    
    async def wait_for_tournament_to_resume(self):
        """Wait for players to start with a countdown for tournament games."""
        start_time = time.time()
        duration = 5

        while time.time() - start_time < duration:
            connected_users_count = await self.redis_ops.get_connected_users_nb()
            if connected_users_count == self.player_nb:
                print("All players connected. Tournament game can start.")
                return True
            
            # Send countdown to frontend
            remaining_time = int(duration - (time.time() - start_time))
            await self.channel_com.send_countdown(remaining_time)
            
            await asyncio.sleep(1)  # Wait a bit before the next check

        # If we reach this point, not all players are ready after the countdown
        print("Not all players were ready for the tournament game within the 30 seconds.")
        await self.channel_com.send_countdown(0)  # Indicate the countdown has finished
        return False

    async def check_for_players_ready(self):
        connected_users_count = await self.redis_ops.get_connected_users_nb()
        if connected_users_count == self.player_nb:
            return True, "Both players connected."
        elif connected_users_count == 0:
            return False, "No player in the room anymore."
        return None, "Waiting for players to start the game..."

    async def check_for_restart_conditions(self):
        """Check condition for game restart waiting."""
        connected_users_count = await self.redis_ops.get_connected_users_nb()
        restart_requests_count = await self.redis_ops.get_restart_requests()
        if restart_requests_count == connected_users_count == self.player_nb:
            return True, "All players in room are ready to restart the game."
        elif connected_users_count == 0:
            return False, "All players in room have left."
        return None, "Waiting for players to restart the game..."
    