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

    async def init_env(self):
        """Initial env setup."""
        self.redis_ops = await RedisOps.create(self.room_name)
        self.channel_com = ChannelCom(self.room_group_name)
        self.game_sync = GameSync(self.redis_ops, self.room_name)

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

        # Init status
        await self.redis_ops.set_game_status(GameStatus.IN_PROGRESS)

        # Send initial data to clients
        await self.channel_com.send_static_data(self.static_data)
        await self.channel_com.send_dynamic_data(\
            await self.redis_ops.get_dynamic_data())
        
        # Delete redis gamelogic flag
        self.redis_ops.del_game_logic_flag()


    def init_static_data(self):
        static_data = {
            "scoreLimit": int(SCORE_LIMIT),
            "canvasHeight": int(SCREEN_HEIGHT),
            "canvasWidth": int(SCREEN_WIDTH),
            "paddleWidth": int(PADDLE_WIDTH),
            "paddleHeight": int(PADDLE_HEIGHT),
            "paddleSpeed": int(PADDLE_SPEED),
            "ballSize": int(BALL_SIZE),
        }
        return static_data

    # -------------------------------CHECK-----------------------------------

    async def is_game_active(self):
        current_status = await self.redis_ops.get_game_status()
        
        if current_status == GameStatus.COMPLETED:
            return False
        elif current_status == GameStatus.SUSPENDED:
            await self.channel_com.send_dynamic_data(\
                await self.redis_ops.get_dynamic_data())
            print(await self.redis_ops.get_dynamic_data())
            return await self.is_game_resuming()

        return True

    async def is_game_resuming(self):
        print("Checking if the game is resuming...")  # Print at the beginning to indicate the method has started
        game_resuming = await self.game_sync.wait_for_players_to_start()
        print(f"Game resuming status: {game_resuming}")  # Print the status of game_resuming

        new_status = GameStatus.IN_PROGRESS if game_resuming else GameStatus.COMPLETED
        print(f"Setting new game status to: {'IN_PROGRESS' if game_resuming else 'COMPLETED'}")  # Print the new status being set

        await self.redis_ops.set_game_status(new_status)  # Set the new status in Redis
        await self.channel_com.send_static_data(self.static_data)  # Send the static data to clients
        print("Static data sent to clients.")  # Print after sending static data

        return game_resuming  # Return the status of game resuming

    # -------------------------------LOOP-----------------------------------

    async def run(self):
        """Running the task"""
        await self.init_env()

        if await self.game_sync.wait_for_players_to_start():
            await self.game_loop()

    async def game_loop(self):
        """The main game loop."""
        await self.init_game()
        last_update_time = time.time()
        print("Game loop started.")

        try:
            while True:
                for player in self.players:
                    await player.get_paddle_from_redis()

                delta_time = await self.game_tick(last_update_time)

                if not await self.is_game_active():
                    break
    
                last_update_time += delta_time
                await asyncio.sleep(1/TICK_RATE)

            if await self.game_sync.wait_for_players_to_restart():
                await self.redis_ops.del_all_restart_requests()
                await self.game_loop()
                    
        except asyncio.CancelledError:
             # Handle cleanup upon asyncio task cancellation
             print("Game loop cancelled. Performing cleanup.")
             self.redis_ops.clear_all_data()
        except Exception as e:
             # Handle other exceptions that might occur
              print(f"An unexpected error occurred: {e}")
              self.redis_ops.clear_all_data()

    async def game_tick(self, last_update_time):
        """Perform a single tick of the game loop."""
        current_time = time.time()
        delta_time = current_time - last_update_time
        
        # Update the ball position in fucntion on vellocity and delta time
        self.ball.update_position(delta_time)

        # Check and handle wall collision
        if self.ball.check_wall_collision():
            self.ball.handle_wall_collision()

        # Check and handle paddle collision
        collision, position = self.ball.check_paddle_collision(self.players)
        if collision:
            self.ball.handle_paddle_collision(position, self.players)
        
        # Check and handle goal scored
        scored, scorer_position = self.ball.check_score()
        if scored:
            self.ball.reset_value()
            await self.players[scorer_position.value].update_score()
            if self.players[scorer_position.value].check_win():
                await self.redis_ops.set_game_status(GameStatus.COMPLETED)
        
        # Set the ball data to Redis
        await self.ball.set_data_to_redis()

        # Send the Redis data to clients
        await self.channel_com.send_dynamic_data(\
            await self.redis_ops.get_dynamic_data())
        
        return delta_time
