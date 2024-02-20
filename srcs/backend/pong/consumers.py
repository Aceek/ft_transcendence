import json
import random
import asyncio
import time
import math
import socket
import aioredis

# from asyncio import sleep
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404

from .game_config import *
from .game_logic import game_logic_task

class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialize_game()

    # -------------------------------CLASS INITIALIZATION--------------------------------

    def initialize_game(self):
        # static variable
        self.paddle_width = PADDLE_WIDTH
        self.paddle_height = PADDLE_HEIGHT
        self.paddle_speed = PADDLE_SPEED
        self.ball_speed_range = BALL_SPEED_RANGE
        self.ball_size = BALL_SIZE
        self.canvas_height = SCREEN_HEIGHT
        self.canvas_width = SCREEN_WIDTH
        self.left_player_score = self.right_player_score = INITIAL_SCORE
        self.score_limit = SCORE_LIMIT
        self.ready_to_play = 0

        # dynamic variable
        self.ball_launched = False
        self.last_update_time = time.time()
        self.game_status = "unstarted"
        self.left_paddle = {"up": False, "down": False, "y": INITIAL_PADDLE_Y}
        self.right_paddle = {"up": False, "down": False, "y": INITIAL_PADDLE_Y}
        self.ball = {
            "x": INITIAL_BALL_X,
            "y": INITIAL_BALL_Y,
            "speedX": random.choice([-self.ball_speed_range, self.ball_speed_range]),
            "speedY": random.choice([-self.ball_speed_range, self.ball_speed_range]),
        }

    # -------------------------------WEBSOCKET CONNECTION-------------------------

    async def connect(self):
        # Updated aioredis connection for version 2.0+
        try:
            # For aioredis v2.0+, use aioredis.from_url to connect
            self.redis = await aioredis.from_url("redis://redis:6379", db=0, encoding="utf-8", decode_responses=True)
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            # Depending on your error handling, you might choose to close the connection
            # await self.close()

         # Example: Store a custom user ID or use Django's authenticated user
        self.user_id = str(self.scope["user"].id if self.scope["user"].is_authenticated else "anonymous")

        # create a room based on the uid of the game
        self.room_name = self.scope["url_route"]["kwargs"]["uid"]
        self.room_group_name = f"pong_room_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Attempt to set the flag indicating this consumer should handle the game logic
        flag_set = await self.redis.setnx("game_logic_flag", "true")
        if flag_set:
            # This consumer will handle the game logic
            self.handle_game_logic = True
            # Set an expiration time for the flag to avoid stale locks
            await self.redis.expire("game_logic_flag", 60)  # Expires in 60 seconds
        else:
            self.handle_game_logic = False

        if self.handle_game_logic:
            asyncio.create_task(game_logic_task(self.room_name))

        await self.accept()

        game_init_data = {
            "type": "game.init",
            "paddleWidth": self.paddle_width,
            "paddleHeight": self.paddle_height,
            "ballSize": self.ball_size,
            "initialLeftPaddleY": self.left_paddle["y"],
            "initialRightPaddleY": self.right_paddle["y"],
            "initialBallPosition": self.ball,
            "initialLeftPlayerScore": self.left_player_score,
            "initialRightPlayerScore": self.right_player_score,
            "gameStatus": self.game_status,
        }

        # Set initial game state in Redis
        game_state_key = f"game_state:{self.room_name}"
        initial_game_state = {
            "paddleWidth": str(self.paddle_width),
            "paddleHeight": str(self.paddle_height),
            "ballSize": str(self.ball_size),
            "initialLeftPaddleY": str(self.left_paddle["y"]),
            "initialRightPaddleY": str(self.right_paddle["y"]),
            "initialBallPositionX": str(self.ball["x"]),
            "initialBallPositionY": str(self.ball["y"]),
            "initialLeftPlayerScore": str(self.left_player_score),
            "initialRightPlayerScore": str(self.right_player_score),
            "status": "active"  # Set the initial status of the game
        }
    
        # Use hmset if your Redis client version supports it, otherwise use hset.
        await self.redis.hset(game_state_key, mapping=initial_game_state)

        # Send the game initialization data to the frontend
        # await self.send(json.dumps(game_init_data))
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "game_init", "message": game_init_data}
        )

        #  send message to verify the connection and player is ready to play
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "start_game"}
        )

        # Start the game loop
        # self.ball_launched = True
        # asyncio.create_task(self.game_loop())

    async def disconnect(self, close_code):
        # Change game status to paused
        print("disconnected")
        # self.game_status = "paused"
        await self.redis.hset(f"game_state:{self.room_name}", "status", "paused")
        
        # Broadcast the game pause to all clients
        pause_message = {
            "type": "broadcast_message",
            "message": {
                "type": "game.paused",
                "data": {"reason": "Player disconnected", "gameStatus": self.game_status},
            },
        }
        await self.channel_layer.group_send(self.room_group_name, pause_message)
        
        # Remove this channel from the group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
        if self.handle_game_logic:
            # Clear the flag as this consumer was responsible for the game logic
            await self.redis.delete("game_logic_flag")

        # Optionally, reset the game or handle the disconnection further
        self.initialize_game()  # Consider when and how to reset game state


    async def receive(self, text_data):
        data = json.loads(text_data)

        delta_time = 0.0

        if data["message"] == "ready_to_play":
            self.ready_to_play += 1
            print("Player is ready to play")
            if self.ready_to_play == 2:
                print("Both players are ready to play")
                self.ball_launched = True
                self.game_status = "ongoing"
                asyncio.create_task(self.game_loop())
        if data["message"] == "paddle_movement":
            await self.handle_paddle_movement(data, delta_time)
        else:
            await self.handle_game_update(delta_time, data)

    # -------------------------------GAME LOOP-----------------------------------

    async def game_loop(self):
        last_update_time = time.time()
        print("Game loop started")

        while True:
            # print("Game loop ongoing")
            current_time = time.time()
            delta_time = current_time - last_update_time

            # Print delta time for debugging
            # print("Delta Time:", delta_time)

            game_state = await self.get_game_state()  # Fetch the current game state from Redis
            if game_state["status"] != "active":
                print("Game paused or stopped, exiting game loop.")
                break  # Exit the loop if the game is not active

            # Update ball position based on game mechanics
            self.update_ball_position(delta_time)

            # Example: Echo the updated positions back to all clients
            await self.send_game_update(delta_time)

            # Calculate the sleep duration to achieve 60 FPS
            target_fps = 60
            target_frame_time = 1.0 / target_fps
            sleep_duration = max(0, target_frame_time - delta_time)

            # Adjust the sleep duration based on the delta time
            await asyncio.sleep(sleep_duration)

            last_update_time = current_time

    async def send_game_update(self, delta_time=0.0):
        await self.handle_game_update(delta_time)
        await self.send_game_state()

    async def get_game_state(self):
    # Example function to fetch the game state from Redis
        game_state_data = await self.redis.hgetall(f"game_state:{self.room_name}")
        return game_state_data

    # -------------------------------PADLLE MOVEMENT-----------------------------

    async def handle_paddle_movement(self, data, delta_time):
        left_paddle_state = data["leftPaddleState"]
        right_paddle_state = data["rightPaddleState"]

        self.update_paddle_position(self.left_paddle, left_paddle_state)
        self.update_paddle_position(self.right_paddle, right_paddle_state)

        await self.send_game_update(delta_time)

    def update_paddle_position(self, paddle_movement, paddle_state):
        # Update movement flags based on paddle state
        paddle_movement["up"] = paddle_state["up"]
        paddle_movement["down"] = paddle_state["down"]

        # Update paddle position based on movement flags
        if paddle_movement["up"]:
            paddle_movement["y"] = max(0, paddle_movement["y"] - self.paddle_speed)
        elif paddle_movement["down"]:
            paddle_movement["y"] = min(
                400 - self.paddle_height, paddle_movement["y"] + self.paddle_speed
            )

    # -------------------------------GAME UPDATE-----------------------------

    async def handle_game_update(self, delta_time, data=None):
        self.update_ball_position(delta_time)
        
        if self.game_status == "paused":
            print("Game status is paused before updating Redis")
        # elif self.game_status == "over":
        #     print("Game status is over before updating Redis")

        # Serializing the ball object as JSON since it's a nested structure
        ball_json = json.dumps(self.ball)
        
        # Creating or updating multiple fields in the hash
        await self.redis.hset(
            f"game_state:{self.room_name}",
            mapping={
                "lpY": self.left_paddle["y"],
                "rpY": self.right_paddle["y"],
                "ball": json.dumps(self.ball),
                "lpS": self.left_player_score,
                "rpS": self.right_player_score,
                "gS": self.game_status
            }
        )

        # # Preparing game update data for sending to clients
        # game_update_data = {
        #     "type": "game.update",
        #     "leftPaddleY": self.left_paddle["y"],
        #     "rightPaddleY": self.right_paddle["y"],
        #     "ball": self.ball,
        #     "leftPlayerScore": self.left_player_score,
        #     "rightPlayerScore": self.right_player_score,
        #     "matchOver": self.match_over,
        # }

        # # Sending the game update data to all clients in the room
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         "type": "game_update",
        #         "message": game_update_data,
        #     },
        # )

    async def send_game_state(self):
        game_state_key = f"game_state:{self.room_name}"
        # Fetching all fields from the game state hash
        game_state_data = await self.redis.hgetall(game_state_key)
        
        # If you've stored some fields as JSON, remember to deserialize them
        if 'ball' in game_state_data:
            game_state_data['ball'] = json.loads(game_state_data['ball'])

        # Convert Redis responses, which are bytes, to a proper format
        game_state_data = {k: v for k, v in game_state_data.items()}
        
        # Convert matchOver back to boolean if stored as int
        if 'mO' in game_state_data:
            game_state_data['gS'] = self.game_status
        
        # Including user_id within game_state_data
        game_state_data['user_id'] = self.user_id

        final_message = {
            "type": "broadcast_message",
            "message": {
                "type": "game.state",
                "data": game_state_data,
            }
        }

        # Using channel_layer to send the game state to all clients in the room
        await self.channel_layer.group_send(self.room_group_name, final_message)


    def update_ball_position(self, delta_time):
        if not self.ball_launched or self.game_status != "ongoing":
            return

        # Update ball's position based on its speed and direction
        self.ball["x"] += self.ball["speedX"] * delta_time
        self.ball["y"] += self.ball["speedY"] * delta_time

        self.check_collisions()
        self.check_scoring()

    # -------------------------------GAME MECHANICS-----------------------------------

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
        if (
            self.left_player_score == self.score_limit
            or self.right_player_score == self.score_limit
        ):
            # Set game state to over
            self.game_status = "over"
            self.ball_launched = False
        else:
            # Continue the game
            self.reset_ball()

    def reset_ball(self):
        # Set the ball to the initial position and choose a new random speed
        self.ball = {
            "x": INITIAL_BALL_X,
            "y": INITIAL_BALL_Y,
            "speedX": random.choice([-self.ball_speed_range, self.ball_speed_range]),
            "speedY": random.choice([-self.ball_speed_range, self.ball_speed_range]),
        }

    # -------------------------------CHANNEL LAYER-----------------------------------

    async def game_init(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))

    async def game_update(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))

    async def start_game(self, event):
        await self.send(text_data=json.dumps({"type": "start_game"}))

    async def broadcast_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event["message"]))