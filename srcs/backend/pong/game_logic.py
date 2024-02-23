import asyncio
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

class GameLogic:
    def __init__(self, room_name):
        self.room_name = room_name
        self.room_group_name = f'pong_room_{room_name}'
        self.channel_layer = get_channel_layer()
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
        self.game_status = GameStatus.NOT_STARTED
        self.players = {
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
        # print(f"-------Initiating static data from Redis: {static_data}") 

    async def update_redis_dynamic_data(self):
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        dynamic_data = {
			"b_x": int(self.ball['x']),
			"b_y": int(self.ball['y']),
			"bs_x": int(self.ball['speedX']),
			"bs_y": int(self.ball['speedY']),
        }
        await self.redis.hset(dynamic_data_key, mapping=dynamic_data)
        # print(f"-------Update dynamic data from Redis: {dynamic_data}")
    
    async def update_redis_game_status(self, new_status: GameStatus):
        self.game_status = new_status
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        await self.redis.hset(dynamic_data_key, "gs", int(self.game_status.value))

        await self.send_redis_game_status_to_client()

    async def send_redis_game_status_to_client(self):
        """
        Send the current game status to the client.
        """
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        game_status_key = "gs"
        
        # Fetch the current game status from Redis
        current_game_status = await self.redis.hget(dynamic_data_key, game_status_key)
        
        current_game_status = GameStatus(int(current_game_status)).name if current_game_status else "UNKNOWN"
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game.status_update",  # Ensure this type matches a handler in your consumer
                "status": current_game_status
            }
        )

    async def reset_paddle_positions(self):
        """
        Reset the paddle positions for both sides to the initial Y coordinate.
        """
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        
        # Reset both paddle positions to the initial Y value
        await self.redis.hset(dynamic_data_key, "lp_y", INITIAL_PADDLE_Y)
        await self.redis.hset(dynamic_data_key, "rp_y", INITIAL_PADDLE_Y)
        
        print(f"Reset both paddle positions to initial Y: {INITIAL_PADDLE_Y}")

    async def reset_score(self):
        """
        Reset the paddle positions for both sides to the initial Y coordinate.
        """
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        
        # Reset both paddle positions to the initial Y value
        await self.redis.hset(dynamic_data_key, "lp_s", INITIAL_SCORE)
        await self.redis.hset(dynamic_data_key, "rp_s", INITIAL_SCORE)
        
        print(f"Reset both paddle positions to initial Y: {INITIAL_PADDLE_Y}")

    async def fetch_redis_paddle_pos(self):
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        lp_y, rp_y = await self.redis.hmget(dynamic_data_key, "lp_y", "rp_y")
        
        # Update the Y positions of the paddles if they exist
        if lp_y is not None:
            self.players["left"]["paddle"]["y"] = int(lp_y)
            # self.left_paddle['y'] = int(lp_y)
        if rp_y is not None:
            self.players["right"]["paddle"]["y"] = int(lp_y)
            # self.right_paddle['y'] = int(rp_y)

    async def fetch_redis_game_status(self):
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        game_status = await self.redis.hget(dynamic_data_key, "gs")

        if game_status is not None:
            self.game_status = GameStatus(int(game_status))
            if self.game_status != GameStatus.IN_PROGRESS:
                print(f"Fetched game status from Redis: {self.game_status}")  # Added print statement
        # else:
        #     print("Game status not found in Redis.")  # Added to handle case where game status is None


    async def update_redis_score(self, player_side):
        """
        Increment the score of the specified player side ('left' or 'right').
        """
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        player_key = "lp_s" if player_side == "left" else "rp_s"
        
        # Increment the score directly in Redis
        await self.redis.hincrby(dynamic_data_key, player_key, 1)

        await self.send_redis_score_to_client(player_side)

    async def wait_for_other_player(self):
        connected_users_set_key = f"game:{self.room_name}:connected_users"
        print(f"Waiting for other players in room: {self.room_name}")
        try:
            await asyncio.wait_for(self._check_for_other_player(connected_users_set_key), timeout=300.0)
            print("Both players connected.")
            return True
        except asyncio.TimeoutError:
            print("Timeout reached while waiting for another player.")
            return False

    async def _check_for_other_player(self, connected_users_set_key):
        while True:
            connected_users_count = await self.redis.scard(connected_users_set_key)
            if connected_users_count >= 2:
                break
            await asyncio.sleep(1)
            
         # ----------------------------REDIS TO CLIENT-----------------------------------

    async def send_redis_static_data_to_client(self):
        static_data_key = f"game:{self.room_name}:static"
        static_data = await self.redis.hgetall(static_data_key)

        # print(f"Sending static game data to client: {static_data}")

        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                "type": "game.static_data", 
                "data": static_data  # Sending the Redis hash map as is
            }
        )

    async def send_redis_dynamic_data_to_client(self):
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        dynamic_data = await self.redis.hgetall(dynamic_data_key)

        # print(f"wSending dynamic game data to client: {dynamic_data}")

        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                "type": "game.dynamic_data", 
                "data": dynamic_data  # Sending the Redis hash map as is
            }
        )

    async def send_redis_score_to_client(self, player_side):
        """
        Send the updated score of the specified player side ('left' or 'right') to the client.
        """
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        score_key = "lp_s" if player_side == "left" else "rp_s"
        
        # Fetch the specific score from Redis
        player_score = await self.redis.hget(dynamic_data_key, score_key)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game.score_update",  # Note the underscore
                "side": player_side,
                "score": player_score
            }
        )

    # -------------------------------GAME LOOP-----------------------------------

    async def run_game_loop(self):
        await self.connect_to_redis()
        await self.init_redis_static_data()
        await self.update_redis_dynamic_data()
        await self.reset_paddle_positions()
        await self.reset_score()

        players_ready = await self.wait_for_other_player()
        if not players_ready:
            print("Not enough players connected. Exiting game loop.")
            return
        
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         "type": "send_start_game_message",  # This corresponds to a handler in your consumer
        #     }
        # )

        await self.send_redis_static_data_to_client()
        await self.send_redis_dynamic_data_to_client()

        last_update_time = time.time()
        await self.update_redis_game_status(GameStatus.IN_PROGRESS)

        print("GAMELOGIC -> LOOP STARTED")
        try:
            while True:
                current_time = time.time()
                delta_time = current_time - last_update_time
                
                await self.fetch_redis_paddle_pos()
                
                # Update ball position only if the game is in progress
                if self.game_status == GameStatus.IN_PROGRESS:
                    self.update_ball_position(delta_time)

                await self.update_redis_dynamic_data()
                await self.send_redis_dynamic_data_to_client()

                for side in ["left", "right"]:
                    try:
                        if self.players[side]["score"]["updated"]:
                            await self.update_redis_score(side)
                            await self.send_redis_score_to_client(side)
                            self.players[side]["score"]["updated"] = False
                    except Exception as e:
                        print(f"Error updating or sending score for {side}: {e}")

                if self.game_status == GameStatus.COMPLETED:
                    await self.update_redis_game_status(GameStatus.COMPLETED)

                #WARNING MAKE INFINITE LOOP
                await self.fetch_redis_game_status()

                if self.game_status == GameStatus.SUSPENDED:
                # Attempt to wait for other player(s) to reconnect or join
                        players_ready = await self.wait_for_other_player()

                        if players_ready:
                            print("Players are ready. Game can resume.")
                            # Optionally, update the game status to IN_PROGRESS or another appropriate status
                            await self.update_redis_game_status(GameStatus.IN_PROGRESS)
                        else:
                            print("Not all players reconnected. Handling game suspension.")
                            # Handle the scenario where not all players reconnected within the timeout
                            # This could involve extending the suspension, ending the game, or other logic
                            continue  # Or use break if you wish to exit the loop instead

                # await self.fetch_redis_game_status()
                if self.game_status != GameStatus.IN_PROGRESS:
                    print("GAMELOGIC -> LOOP EXITED status", self.game_status)
                    await self.update_redis_game_status(self.game_status)
                    break

                # Calculate the sleep duration to achieve 60 FPS
                target_fps = 60
                target_frame_time = 1.0 / target_fps
                sleep_duration = max(0, target_frame_time - delta_time)

                # Adjust the sleep duration based on the delta time
                await asyncio.sleep(sleep_duration)

                last_update_time = current_time

        except asyncio.CancelledError:
            # Perform any necessary cleanup after cancellation
            print("Game loop was cancelled, cleaning up")

    # -------------------------------GAME MECHANICS-----------------------------------

    def update_ball_position(self, delta_time):
        if self.game_status != GameStatus.IN_PROGRESS:
            return

        # Calculate predicted next position
        next_x = self.ball["x"] + self.ball["speedX"] * delta_time
        next_y = self.ball["y"] + self.ball["speedY"] * delta_time

        # Check for wall collisions based on predicted position
        if next_y - self.ball_size / 2 < 0 or next_y + self.ball_size / 2 > self.canvas_height:
            self.handle_wall_collision()
            # Adjust ball position to the edge of the wall
            adjusted_y = max(self.ball_size / 2, min(next_y, self.canvas_height - self.ball_size / 2))
            self.ball["y"] = adjusted_y
        else:
            # No collision, update position normally
            self.ball["x"] = next_x
            self.ball["y"] = next_y

        self.check_collisions()
        self.check_scoring()

    def check_collisions(self):
        # Check for collisions with paddles
        if (
            self.ball["x"] - self.ball_size / 2 < self.paddle_width
            and self.players["left"]["paddle"]["y"]
            < self.ball["y"]
            < self.players["left"]["paddle"]["y"]  + self.paddle_height
        ) or (
            self.ball["x"] + self.ball_size / 2 > self.canvas_width - self.paddle_width
            and self.players["right"]["paddle"]["y"]
            < self.ball["y"]
            < self.players["right"]["paddle"]["y"]  + self.paddle_height
        ):
            self.handle_paddle_collision()

        # Check for collisions with walls
        if (

            self.ball["y"] - self.ball_size / 2 < 0
            or self.ball["y"] + self.ball_size / 2 > self.canvas_height
        ):
            self.handle_wall_collision()
            print("wall collison")

    def handle_paddle_collision(self):
        # Determine which paddle was hit
        if self.ball["x"] < self.canvas_width / 2:
            paddle = self.players["left"]["paddle"]
            direction = 1
        else:
            paddle = self.players["right"]["paddle"]
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
            self.update_score("right")
        elif self.ball["x"] > self.canvas_width + self.ball_size / 2:
            self.update_score("left")

    def update_score(self, player_side):
        """
        Updates the score for the specified player side ('left' or 'right') and checks for game over.
        
        Args:
            player_side (str): The side of the player ('left' or 'right') to update the score for.
        """
        # Increment the score based on the player side
        self.players[player_side]["score"]["value"] += 1

        # Mark that the score has been updated
        self.players[player_side]["score"]["updated"] = True

        # Check if the updated score results in the game being over
        self.check_game_over()

    def check_game_over(self):
        if (
            self.players["left"]["score"]["value"] >= self.score_limit
            or self.players["left"]["score"]["value"] >= self.score_limit
        ):
            print(f"Game Over: Left score {self.players['left']['score']['value']}, Right score {self.players['right']['score']['value']}, Score limit {self.score_limit}")
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
