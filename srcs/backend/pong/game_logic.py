import json
import aioredis
import random
import asyncio
import time
import math

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .game_config import *
from .game_status import GameStatus
from .game_utils import *
from .game_mechanics import *
from .game_sync import GameSync
from .game_score import *
from .redis_ops import RedisOps

class GameLogic:
    def __init__(self, room_name):
        self.room_name = room_name
        self.room_group_name = f'pong_room_{room_name}'
        self.channel_layer = get_channel_layer()

    # -------------------------------INIT-----------------------------------

    async def init_env(self):
        """Initial env setup."""
        self.redis_ops = await RedisOps.create(self.room_name)
        self.game_sync = GameSync(self.redis_ops.connection, self.room_name)

    async def init_game(self):
        """Initial game setup."""
        self.game_status = GameStatus.NOT_STARTED
        self.players = self.init_players()
        self.ball = self.init_ball() 
        await self.set_static_data()
        await self.set_ball()
        await self.set_scores()
        await self.set_paddles()
        await self.send_channel_static_data()

    def init_players(self):
        players = {
            "left": {
                "score": {
                    "value": INITIAL_SCORE,
                    "updated": False
                },
                "paddle": {
                    "y": INITIAL_PADDLE_Y
                }
            },
            "right": {
                "score": {
                    "value": INITIAL_SCORE,
                    "updated": False
                },
                "paddle": {
                    "y": INITIAL_PADDLE_Y
                }
            }
        }
        return players
    
    def init_ball(self):
        ball = {
            "x": INITIAL_BALL_X,
            "y": INITIAL_BALL_Y,
            "speedX": random.choice([-BALL_SPEED_RANGE, BALL_SPEED_RANGE]),
            "speedY": random.choice([-BALL_SPEED_RANGE, BALL_SPEED_RANGE]),
        }
        return ball
    

    # -----------------------------REDIS SETTERS----------------------------------
        
    async def set_static_data(self):
        static_data = {
            "scoreLimit": int(SCORE_LIMIT),
            "canvasHeight": int(SCREEN_HEIGHT),
            "canvasWidth": int(SCREEN_WIDTH),
            "paddleWidth": int(PADDLE_WIDTH),
            "paddleHeight": int(PADDLE_HEIGHT),
            "paddleSpeed": int(PADDLE_SPEED),
            "ballSize": int(BALL_SIZE),
        }
        await self.redis_ops.set_static_data(self.room_name, static_data)

    async def set_ball(self):
        dynamic_data = {
			"b_x": int(self.ball['x']),
			"b_y": int(self.ball['y']),
			"bs_x": int(self.ball['speedX']),
			"bs_y": int(self.ball['speedY']),
        }
        await self.redis_ops.set_dynamic_data(self.room_name, dynamic_data)
        
    async def set_score(self, side):
        key = "lp_s" if side == "left" else "rp_s"
        score = self.players[side]["score"]["value"]

        await self.redis_ops.set_dynamic_value(self.room_name, key, score)

    async def set_scores(self):
        await self.redis_ops.set_dynamic_value(self.room_name, "lp_s", self.players["left"]["score"]["value"])
        await self.redis_ops.set_dynamic_value(self.room_name, "rp_s", self.players["left"]["score"]["value"])
    
    async def set_paddles(self):
        await self.redis_ops.set_dynamic_value(self.room_name, "lp_y", self.players["left"]["paddle"]["y"])
        await self.redis_ops.set_dynamic_value(self.room_name, "rp_y", self.players["left"]["paddle"]["y"])

    async def set_game_status(self, new_status: GameStatus):
        self.game_status = new_status
        await self.redis_ops.set_dynamic_value(self.room_name, "gs", int(new_status.value))
        
    # -----------------------------REDIS GETTERS----------------------------------
        
    async def get_paddles(self):
        """
        Get the Y positions of the paddles from Redis and update the players' positions.
        """
        # Fetch the Y positions using the get_dynamic_value method
        lp_y = await self.redis_ops.get_dynamic_value(self.room_name, "lp_y")
        rp_y = await self.redis_ops.get_dynamic_value(self.room_name, "rp_y")
        
        # Update the Y positions of the paddles if they exist
        if lp_y is not None:
            self.players["left"]["paddle"]["y"] = int(lp_y)
        if rp_y is not None:
            self.players["right"]["paddle"]["y"] = int(rp_y)

    # -----------------------------CHANNEL SEND----------------------------------
            
    async def send_channel_static_data(self):
        # Fetch static data using the RedisOps class method
        static_data = await self.redis_ops.get_static_data(self.room_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game.static_data",
                "data": static_data  # Sending the Redis hash map as is
            }
        )

    async def send_channel_dynamic_data(self):
        # Fetch dynamic data using the RedisOps class method
        dynamic_data = await self.redis_ops.get_dynamic_data(self.room_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game.dynamic_data",
                "data": dynamic_data  # Sending the Redis hash map as is
            }
        )

    # -------------------------------CHECK-----------------------------------

    async def check_game_completed(self):
        """Handle changes in game status, including suspensions and completions."""
        if self.game_status == GameStatus.COMPLETED:
            return True

        if await self.check_game_status_change():
            await self.send_channel_dynamic_data()

        if self.game_status == GameStatus.SUSPENDED:
            if await self.game_sync.wait_for_players_to_start():
                await self.set_game_status(GameStatus.IN_PROGRESS)
                await self.send_channel_static_data()
                return False
            return True
        return False

    async def check_game_status_change(self):
        current_status = await self.redis_ops.get_dynamic_value(self.room_name, "gs")
        if current_status:
            current_status = GameStatus(int(current_status))
            if current_status != self.game_status:
                self.game_status = current_status
                return True
        return False  

    async def check_score_updates(self):
        """Handle score updates for each side."""
        for side in ["left", "right"]:
            try:
                if self.players[side]["score"]["updated"]:
                    await self.set_score(side)
                    self.players[side]["score"]["updated"] = False
            except Exception as e:
                print(f"Error updating or sending score for {side}: {e}")

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
        await self.set_game_status(GameStatus.IN_PROGRESS)
        await self.send_channel_dynamic_data()
        last_update_time = time.time()

        while True:
            await self.get_paddles()
            delta_time = self.game_tick(last_update_time)
            await self.check_score_updates()

            if await self.check_game_completed():
                await self.set_game_status(GameStatus.COMPLETED)
                await self.send_channel_dynamic_data()
                break
            else:
                await self.set_ball()
                await self.send_channel_dynamic_data()

            last_update_time += delta_time
            await asyncio.sleep(1/30)

        if await self.game_sync.wait_for_players_to_restart():
            await self.game_loop()

    def game_tick(self, last_update_time):
        """Perform a single tick of the game loop."""
        current_time = time.time()
        delta_time = current_time - last_update_time
        
        if self.game_status == GameStatus.IN_PROGRESS:
            self.ball = update_ball(self.ball, self.players, delta_time)
            scored, self.players = check_scoring(self.ball, self.players)
            if scored:
                if check_game_over(self.players):
                    self.game_status = GameStatus.COMPLETED
                else:
                    self.ball = self.init_ball()
        return delta_time
