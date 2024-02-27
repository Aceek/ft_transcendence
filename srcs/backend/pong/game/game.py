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
    def __init__(self, room_name):
        self.room_name = room_name
        self.room_group_name = f'pong_room_{room_name}'

    # -------------------------------INIT-----------------------------------

    async def init_env(self):
        """Initial env setup."""
        self.redis_ops = await RedisOps.create(self.room_name)
        self.channel_com = ChannelCom(self.room_name)
        self.game_sync = GameSync(self.redis_ops, self.room_name)

    async def init_game(self):
        """Initial game setup."""
        self.static_data = self.init_static_data() 
        self.players = [Player(PlayerPosition.LEFT, self.redis_ops), 
                        Player(PlayerPosition.RIGHT, self.redis_ops)]
        for player in self.players:
                await player.set_data_to_redis()
        self.ball = Ball(self.redis_ops) 
        await self.ball.set_data_to_redis()

        await self.redis_ops.set_game_status(GameStatus.NOT_STARTED)
        await self.redis_ops.set_static_data(self.static_data)
        await self.channel_com.send_static_data(self.static_data)

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
        
        if current_status == GameStatus.SUSPENDED:
            dynamic_data = await self.redis_ops.get_dynamic_data()
            await self.channel_com.send_dynamic_data(dynamic_data)
            return await self.is_game_resuming()
        
        return True

    async def is_game_resuming(self):
        game_resuming = await self.game_sync.wait_for_players_to_start()
        new_status = GameStatus.IN_PROGRESS if game_resuming else GameStatus.COMPLETED
        
        await self.redis_ops.set_game_status(new_status)
        await self.channel_com.send_static_data(self.static_data)
        
        return game_resuming

    # -------------------------------LOOP-----------------------------------

    async def run(self):
        """Running the task"""
        await self.init_env()

        if await self.game_sync.wait_for_players_to_start():
            await self.game_loop()

    async def game_loop(self):
        """The main game loop."""
        print("GAMELOGIC -> LOOP STARTED")

        await self.init_game()
        await self.redis_ops.set_game_status(GameStatus.IN_PROGRESS)
        dynamic_data = await self.redis_ops.get_dynamic_data()
        await self.channel_com.send_dynamic_data(dynamic_data)
        last_update_time = time.time()

        try:
            while True:
                for player in self.players:
                    await player.get_paddle_from_redis()

                delta_time = await self.game_tick(last_update_time)

                if not await self.is_game_active():
                    break

                await self.ball.set_data_to_redis()
                dynamic_data = await self.redis_ops.get_dynamic_data()
                await self.channel_com.send_dynamic_data(dynamic_data)
    
                last_update_time += delta_time
                await asyncio.sleep(1/TICK_RATE)

            if await self.game_sync.wait_for_players_to_restart():
                await self.redis_ops.clear_all_restart_requests()
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
                dynamic_data = await self.redis_ops.get_dynamic_data()
                await self.channel_com.send_dynamic_data(dynamic_data)
        
        return delta_time
