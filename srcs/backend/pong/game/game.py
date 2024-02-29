import asyncio
import time

from .ball import Ball
from .player import Player
from .config import *
from .enum import GameStatus, PlayerPosition
from .sync import GameSync
from .channel_com import ChannelCom
from ..redis.redis_ops import RedisOps

class GameLogic:
    def __init__(self, room_name, room_group_name):
        self.room_name = room_name
        self.room_group_name = room_group_name

    # -------------------------------INIT-----------------------------------

    def init_static_data(self):
        static_data = {
            "canvasHeight": int(SCREEN_HEIGHT),
            "canvasWidth": int(SCREEN_WIDTH),
            "paddleWidth": int(PADDLE_WIDTH),
            "paddleHeight": int(PADDLE_HEIGHT),
            "paddleSpeed": int(PADDLE_SPEED),
            "paddleBorderDistance": int(PADDLE_DISTANCE_FROM_BORDER),
            "ballSize": int(BALL_SIZE),
        }
        return static_data
    
    async def init_env(self):
        """Initial env setup."""
        self.redis_ops = await RedisOps.create(self.room_name)
        self.channel_com = ChannelCom(self.room_group_name)
        self.game_sync = GameSync(self.redis_ops, self.room_name)

        # Delete redis gamelogic flag
        await self.redis_ops.del_game_logic_flag()
        
    async def init_game(self):
        """Initial game setup."""
        # Init static data
        self.static_data = self.init_static_data() 
        await self.redis_ops.set_static_data(self.static_data)

        # Init players
        self.players = [Player(PlayerPosition.LEFT, self.redis_ops), 
                        Player(PlayerPosition.RIGHT, self.redis_ops)]
        for player in self.players:
                await player.set_data_to_redis()

        # Init ball
        self.ball = Ball(self.redis_ops) 
        await self.ball.set_data_to_redis()

        # Send data to first client and set the game to not started
        await self.get_static_data_and_send()
        await self.get_dynamic_data_and_send()

    # ---------------------------DATA UPDATES-----------------------------------

    async def get_static_data_and_send(self):
        """Centralized method to send dynamic data."""
        static_data = await self.redis_ops.get_static_data()
        await self.channel_com.send_static_data(static_data)

    async def get_dynamic_data_and_send(self):
        """Centralized method to send dynamic data."""
        dynamic_data = await self.redis_ops.get_dynamic_data()
        await self.channel_com.send_dynamic_data(dynamic_data)

    async def update_game_status_and_notify(self, new_status):
        """Updates game status and sends dynamic data if necessary."""
        await self.redis_ops.set_game_status(new_status)
        await self.get_dynamic_data_and_send()

    # -------------------------------LAUNCHER-----------------------------------

    async def launch_game(self):
        """Launch game."""    
        await self.countdown()

        # If a client disconnect during the countdown, the launchher  restart to wait for a reconnection
        if await self.redis_ops.get_game_status() == GameStatus.SUSPENDED:
            if await self.game_sync.wait_for_players_to_start():
                await self.update_game_status_and_notify(GameStatus.NOT_STARTED)
                await self.launch_game()
        
        await self.update_game_status_and_notify(GameStatus.IN_PROGRESS)
        self.last_update_time = time.time()

    async def countdown(self, duration=3):
        """Handles the countdown logic."""
        print(f"Countdown starting for {duration} seconds.")
        for i in range(duration, 0, -1):
            await self.channel_com.send_countdown(i)
            print(f"Countdown: {i}")
            await asyncio.sleep(1)
        await self.channel_com.send_countdown(0)
        print("Countdown finished.")

    # -------------------------CHECK GAME STATE-----------------------------------

    async def is_game_active(self):
        current_status = await self.redis_ops.get_game_status()
        
        if current_status == GameStatus.COMPLETED:
            return False
        elif current_status == GameStatus.SUSPENDED:
            # Notify all the clients the game is suspendended
            await self.get_dynamic_data_and_send()
            return await self.is_game_resuming()
        return True

    async def is_game_resuming(self):
        print("Checking if the game is resuming...")
        if await self.game_sync.wait_for_players_to_start():
            await self.update_game_status_and_notify(GameStatus.NOT_STARTED)
            await self.launch_game()
            return True

        await self.update_game_status_and_notify(GameStatus.COMPLETED)
        return False

    # -------------------------------LOOP-----------------------------------

    async def run(self):
        """Running the task"""
        await self.init_env()
        await self.init_game()

        # Notify the first client that the init is successful
        await self.update_game_status_and_notify(GameStatus.NOT_STARTED)

        if await self.game_sync.wait_for_players_to_start():
            await self.game_loop()

    async def game_loop(self):
        """The main game loop."""
        await self.launch_game()

        try:
            print("Game loop started.")
            while True:
                current_time = time.time()
                delta_time = current_time - self.last_update_time
                self.last_update_time = current_time

                if not await self.is_game_active():
                    break

                await self.game_tick(delta_time)

                await asyncio.sleep(1/TICK_RATE)

            if await self.game_sync.wait_for_players_to_restart():
                await self.redis_ops.del_all_restart_requests()
                await self.init_game()
                await self.game_loop()
            
        except asyncio.CancelledError:
             # Handle cleanup upon asyncio task cancellation
             await self.redis_ops.clear_all_data()
             print("Game loop cancelled. Performing cleanup.")
        except Exception as e:
             # Handle other exceptions that might occur
              await self.redis_ops.clear_all_data()
              print(f"An unexpected error occurred: {e}")

    async def game_tick(self, delta_time):
        """Perform a single tick of the game lop."""
        # Update the ball position in fucntion on vellocity and delta time
        self.ball.update_position(delta_time)

        # Check and handle wall collision
        if self.ball.check_wall_collision():
            self.ball.handle_wall_bounce()

        # Retrieve paddle position from players
        for player in self.players:
            await player.get_paddle_from_redis()

        # Check and handle paddle collision
        collision, position = self.ball.check_paddle_collision(self.players)
        if collision:
            self.ball.handle_paddle_bounce_calculation(position, self.players)
        
        # Check and handle goal scored
        scored, scorer_position = self.ball.check_score()
        if scored:
            self.ball.reset_value()
            await self.players[scorer_position.value].update_score()
            if self.players[scorer_position.value].check_win():
                await self.update_game_status_and_notify(GameStatus.COMPLETED)
        
        # Set the ball data to Redis
        await self.ball.set_data_to_redis()

        # Broadcast the current game data to all clients
        await self.get_dynamic_data_and_send()
        