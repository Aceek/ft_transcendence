import asyncio
import time

from .ball import Ball
from .player import Player
from .config import *
from .enum import GameStatus, PlayerPosition
from .mechanics import *
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
                await player.set_to_redis()
        self.ball = Ball(self.redis_ops) 
        await self.ball.set_to_redis()

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
    
    # def init_players(self):
    #     players = {
    #         "left": {
    #             "score": {
    #                 "value": INITIAL_SCORE,
    #                 "updated": False
    #             },
    #             "paddle": {
    #                 "y": INITIAL_PADDLE_Y
    #             }
    #         },
    #         "right": {
    #             "score": {
    #                 "value": INITIAL_SCORE,
    #                 "updated": False
    #             },
    #             "paddle": {
    #                 "y": INITIAL_PADDLE_Y
    #             }
    #         }
    #     }
    #     return players
    
    # def init_ball(self):
    #     ball = {
    #         "x": INITIAL_BALL_X,
    #         "y": INITIAL_BALL_Y,
    #         "vx": random.choice([-BALL_SPEED_RANGE, BALL_SPEED_RANGE]),
    #         "vy": random.choice([-BALL_SPEED_RANGE, BALL_SPEED_RANGE]),
    #     }
    #     return ball
    
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

    # async def check_score_updates(self):
    #     """Handle score updates for each side."""
    #     for side in ["left", "right"]:
    #         if self.players[side]["score"]["updated"]:
    #             await self.redis_ops.set_score(, side,
    #                                             self.players[side]["score"]["value"])
    #             self.players[side]["score"]["updated"] = False
    #             await self.check_score_limit(side)

    # async def check_score_limit(self, side):
    #     """Check if the score limit is reached; update game status or reset ball."""
    #     if self.players[side]["score"]["value"] >= SCORE_LIMIT:
    #         await self.redis_ops.set_game_status(, GameStatus.COMPLETED)
    #         dynamic_data = await self.redis_ops.get_dynamic_data()
    #         await self.channel_com.send_dynamic_data(dynamic_data)
    #         print("Game completed due to score limit reached.")

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

                delta_time = self.game_tick(last_update_time)
                # await self.check_score_updates()

                if not await self.is_game_active():
                    break

                await self.ball.set_to_redis()
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

    def game_tick(self, last_update_time):
        """Perform a single tick of the game loop."""
        current_time = time.time()
        delta_time = current_time - last_update_time
        
        update_ball(self.ball, self.players, delta_time)
        
        return delta_time
