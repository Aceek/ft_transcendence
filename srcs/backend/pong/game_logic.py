import asyncio
import json
import aioredis
import random
import asyncio
import time
import math

from .game_config import *
from .game_status import GameStatus

class GameLogic:
    def __init__(self, room_name):
        self.room_name = room_name
        self.game_state_key = f"game_state:{room_name}"
       
        #---CONSTANT VAR---
        self.score_limit = SCORE_LIMIT
        self.canvas_height = SCREEN_HEIGHT
        self.canvas_width = SCREEN_WIDTH
        #to be send to client
        self.paddle_width = PADDLE_WIDTH
        self.paddle_height = PADDLE_HEIGHT
        self.paddle_speed = PADDLE_SPEED
        self.ball_size = BALL_SIZE

        #---DYNAMIC VAR---
        self.ready_to_play = 0
        self.game_status = GameStatus.NOT_STARTED
        self.left_player_score = self.right_player_score = INITIAL_SCORE
        self.left_paddle = {"up": False, "down": False, "y": INITIAL_PADDLE_Y}
        self.right_paddle = {"up": False, "down": False, "y": INITIAL_PADDLE_Y}
        self.ball = {
            "x": INITIAL_BALL_X,
            "y": INITIAL_BALL_Y,
            "speedX": random.choice([-BALL_SPEED_RANGE, BALL_SPEED_RANGE]),
            "speedY": random.choice([-BALL_SPEED_RANGE, BALL_SPEED_RANGE]),
        }

    # -------------------------------REDIS-----------------------------------

    async def connect_to_redis(self):
        self.redis = await aioredis.from_url("redis://redis:6379", db=0, encoding="utf-8", decode_responses=True)

    async def init_redis_static_data(self):
        static_data_key = f"game:{self.room_name}:static"
        static_data = {
            "scoreLimit": int(SCORE_LIMIT),
            "canvasHeight": int(SCREEN_HEIGHT),
            "canvasWidth": int(SCREEN_WIDTH),
            "paddleWidth": int(PADDLE_WIDTH),
            "paddleHeight": int(PADDLE_HEIGHT),
            "paddleSpeed": int(PADDLE_SPEED),
            "ballSize": int(BALL_SIZE),
        }
        await self.redis.hset(static_data_key, mapping=static_data)
        print(f"-------Initiating static data from Redis: {static_data}") 

    async def update_redis_dynamic_data(self):
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        dynamic_data = {
            # "gs": int(self.game_status.value),
            "ls": int(self.left_player_score),
            "rs": int(self.right_player_score),
            "lp": json.dumps(self.left_paddle),
            "rp": json.dumps(self.right_paddle),
            "ball": json.dumps(self.ball),
        }
        await self.redis.hset(dynamic_data_key, mapping=dynamic_data)
        print(f"-------Update dynamic data from Redis: {dynamic_data}") 
    
    async def update_redis_game_status(self, new_status: GameStatus):
        self.game_status = new_status
        # print(f"-------Game status updated to: {self.game_status}") 
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        await self.redis.hset(dynamic_data_key, "gs", int(self.game_status.value))
        print(f"-------Game status updated to: {self.game_status}") 

    async def fetch_redis_dynamic_data(self):
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        dynamic_data = await self.redis.hgetall(dynamic_data_key)

        # Deserialize JSON stored fields
        if 'lp' in dynamic_data:
            self.left_paddle = json.loads(dynamic_data['lp'])
        if 'rp' in dynamic_data:
            self.right_paddle = json.loads(dynamic_data['rp'])
        if 'ball' in dynamic_data:
            self.ball = json.loads(dynamic_data['ball'])

        # Assign other data directly
        if 'ls' in dynamic_data:
            self.left_player_score = int(dynamic_data["ls"])
        if 'rs' in dynamic_data:
            self.right_player_score = int(dynamic_data["rs"])
        # if 'gs' in dynamic_data:
        #     self.game_status = GameStatus(int(dynamic_data["gs"]))

        print(f"-------Fetched dynamic data from Redis: {dynamic_data}")

    async def fetch_redis_game_status(self):
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        game_status = await self.redis.hget(dynamic_data_key, "gs")

        if game_status is not None:
            self.game_status = GameStatus(int(game_status))
            print(f"-------Game status fetched from Redis: {self.game_status}")
        else:
            print("-------Game status not found in Redis.")

    # -------------------------------GAME LOOP-----------------------------------

    async def run_game_loop(self):
        await self.connect_to_redis()
        await self.init_redis_static_data()
        await self.update_redis_dynamic_data()

        last_update_time = time.time()
        self.game_status = GameStatus.IN_PROGRESS
        # await self.update_redis_game_status(GameStatus.IN_PROGRESS)
        print("--------GS before loop", self.game_status)

        while True:
        # while True:
            current_time = time.time()
            delta_time = current_time - last_update_time
            
            # game_state = await self.redis.hgetall(self.game_state_key)
            # if game_state["gameStatus"] != "active":
            #     print("Game not in progress, waiting...")
            #     await asyncio.sleep(1)  # Wait a bit before checking again
            #     continue
            await self.fetch_redis_dynamic_data()
            
            print("-------game status: ", self.game_status)
            # Update game state logic here
            self.update_ball_position(delta_time)

                # Increment and print the loop counter
            # print(f"-------score: {self.left_player_score} vs {self.right_player_score}")
            print(f"-------Ball's position -> X: {self.ball['x']}, Y: {self.ball['y']}")

            await self.update_redis_dynamic_data()
            
            # Example: Echo the updated positions back to all clients
            # await self.send_game_update(delta_time)

            # Example: Echo the updated positions back to all clients
            # await self.send_game_update(delta_time)

            # Calculate the sleep duration to achieve 60 FPS
            target_fps = 1
            target_frame_time = 1.0 / target_fps
            sleep_duration = max(0, target_frame_time - delta_time)

            # Adjust the sleep duration based on the delta time
            await asyncio.sleep(sleep_duration)

            last_update_time = current_time

            # await self.fetch_redis_game_status()
            if self.game_status == GameStatus.COMPLETED:
                print("Game over. Exiting game loop.")
                await self.update_redis_game_status(GameStatus.COMPLETED)
                break  # Exit the loop


    # -------------------------------GAME MECHANICS-----------------------------------

    def update_ball_position(self, delta_time):
        print("-------Game status update ball func: ", self.game_status)
        if self.game_status != GameStatus.IN_PROGRESS:
        # if not self.ball_launched or self.game_status != "active":
            # print("ball not launched")
            print("-------noGAME: ", self.game_status)
            return

        # Update ball's position based on its speed and direction
        self.ball["x"] += self.ball["speedX"] * delta_time
        self.ball["y"] += self.ball["speedY"] * delta_time

        self.check_collisions()
        self.check_scoring()

    def check_collisions(self):
        # Check for collisions with paddles
        if (
            self.ball["x"] - self.ball_size / 2 < self.paddle_width
            and self.left_paddle["y"]
            < self.ball["y"]
            < self.left_paddle["y"] + self.paddle_height
        ) or (
            self.ball["x"] + self.ball_size / 2 > self.canvas_width - self.paddle_width
            and self.right_paddle["y"]
            < self.ball["y"]
            < self.right_paddle["y"] + self.paddle_height
        ):
            self.handle_paddle_collision()

        # Check for collisions with walls
        if (
            self.ball["y"] - self.ball_size / 2 < 0
            or self.ball["y"] + self.ball_size / 2 > self.canvas_height
        ):
            self.handle_wall_collision()

    def handle_paddle_collision(self):
        # Determine which paddle was hit
        if self.ball["x"] < self.canvas_width / 2:
            paddle = self.left_paddle
            direction = 1
        else:
            paddle = self.right_paddle
            direction = -1

        # Calculate the relative position of the collision point on the paddle
        relative_collision_position = (
            self.ball["y"] - paddle["y"]
        ) / self.paddle_height

        # Calculate the new angle of the ball's trajectory based on the relative position
        angle = (relative_collision_position - 0.5) * math.pi / 2

        # Update the ball's speed components based on the new angle
        speed_magnitude = math.sqrt(self.ball["speedX"] ** 2 + self.ball["speedY"] ** 2)
        self.ball["speedX"] = speed_magnitude * math.cos(angle) * direction
        self.ball["speedY"] = speed_magnitude * math.sin(angle) * direction

    def handle_wall_collision(self):
        self.ball["speedY"] *= -1

    # -------------------------------GAME STATE-----------------------------------

    def check_scoring(self):
        # Check for scoring (ball crossing left or right border)
        if self.ball["x"] < 0 - self.ball_size / 2:
            self.score_for_right_player()
        elif self.ball["x"] > self.canvas_width + self.ball_size / 2:
            self.score_for_left_player()

    def score_for_left_player(self):
        self.left_player_score += 1
        self.check_game_over()

    def score_for_right_player(self):
        self.right_player_score += 1
        self.check_game_over()

    def check_game_over(self):
        # print("GO check")
        # Check if any player has reached the maximum score (10)
        print(f"-------------Checking game over. Left player score: {self.left_player_score}, Right player score: {self.right_player_score}, Score limit: {self.score_limit}")
        if (
            self.left_player_score >= self.score_limit
            or self.right_player_score >= self.score_limit
        ):
            # Set game state to over
            self.game_status = GameStatus.COMPLETED
        else:
            # Continue the game
            self.reset_ball()

    def reset_ball(self):
        # Set the ball to the initial position and choose a new random speed
        self.ball = {
            "x": INITIAL_BALL_X,
            "y": INITIAL_BALL_Y,
            "speedX": random.choice([-BALL_SPEED_RANGE, BALL_SPEED_RANGE]),
            "speedY": random.choice([-BALL_SPEED_RANGE, BALL_SPEED_RANGE]),
        }
