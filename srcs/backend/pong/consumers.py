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
from .game_logic import GameLogic
from .game_status import GameStatus


class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ready_to_play = 0
        self.game_status = GameStatus.NOT_STARTED
        self.paddle_side = None

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

        await self.accept()

        # Example: Store a custom user ID or use Django's authenticated user
        self.user_id = str(self.scope["user"].id if self.scope["user"].is_authenticated else "anonymous")

        # create a room based on the uid of the game
        self.room_name = self.scope["url_route"]["kwargs"]["uid"]
        self.room_group_name = f"pong_room_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            
        connected_clients_set_key = f"game:{self.room_name}:connected_users"

        # Add this user ID to the set of connected users
        await self.redis.sadd(connected_clients_set_key, self.user_id)
        
        # Determine paddle assignment based on the number of connected clients
        connected_clients = await self.redis.scard(connected_clients_set_key)

        if connected_clients == 1:
            self.paddle_side = "left"
        else:
            self.paddle_side = "right"
        
        # After assigning the paddle side, notify the client
        await self.send_paddle_side_assignment()

        print("CONSUMER -> check connected : ", self.user_id)
        print("CONSUMER -> nb connected : ", connected_clients)

        await self.attempt_to_acquire_game_logic_control()

        if self.handle_game_logic:
            self.game_logic_instance = GameLogic(self.room_name)
            self.game_logic_task = asyncio.create_task(self.game_logic_instance.run())

    async def disconnect(self, close_code):
        print(f"CONSUMER -> DISCONNECT for client: {self.user_id}")
        if self.handle_game_logic:
                flag_key = f"game_logic_flag:{self.room_name}"
                await self.redis.delete(flag_key)
        
        # Withdraw this user ID from the set of connected users
        connected_clients_set_key = f"game:{self.room_name}:connected_users"
        await self.redis.srem(connected_clients_set_key, self.user_id)
        print(f"Removed user {self.user_id} from connected users in room: {self.room_name}")
        
        # if hasattr(self, 'game_logic_task') and not self.game_logic_task.done():
        #     self.game_logic_task.cancel()
        #     try:
        #         # Wait for the task to be cancelled
        #         # This ensures any cleanup within the task can complete
        #         await self.game_logic_task
        #     except asyncio.CancelledError:
        #         # The task was cancelled, so any necessary cleanup should be done here
        #         print(f"Game logic task for {self.user_id} was cancelled.")

        await self.update_redis_game_status(GameStatus.SUSPENDED)
        
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self, text_data):
        data = json.loads(text_data)

        # # Handle "ready_to_play" message
        # if "message" in data and data["message"] == "ready_to_play":
        #     print("Player is ready to play : ", self.user_id)
        #     # self.game_loop_task = asyncio.create_task(self.game_loop())

        # Handle "paddle_position_update" message
        if "type" in data and data["type"] == "paddle_position_update":
            paddle_y = data.get('PaddleY')
            if paddle_y is not None:
                # print(f"Received paddle position update: {paddle_y}")
                # Update game logic with new paddle position
                if self.paddle_side == "left":
                    await self.update_redis_paddle_position('left', paddle_y)
                elif self.paddle_side == "right":
                    await self.update_redis_paddle_position('right', paddle_y)
                else:
                    print("Game logic instance not found or not initialized")
        else:
            print("Received unknown message type or missing key.")


    async def attempt_to_acquire_game_logic_control(self):
        flag_key = f"game_logic_flag:{self.room_name}"
        flag_set = await self.redis.setnx(flag_key, "true")
        if flag_set:
            # This consumer handles the game logic for the room
            self.handle_game_logic = True
            # Optionally, set an expiration time for the flag
            await self.redis.expire(flag_key, 60)  # Expires in 60 seconds
        else:
            self.handle_game_logic = False

    # -------------------------------PADLLE UPDATE-----------------------------------
    
    async def send_paddle_side_assignment(self):
        """
        Sends a message to the connected client with their paddle side assignment.
        """
        if self.paddle_side is not None:
            await self.send(text_data=json.dumps({
                'type': 'game.paddle_side',
                'paddle_side': self.paddle_side
            }))
        else:
            print(f"No paddle side assigned for user: {self.user_id}")


    async def update_redis_paddle_position(self, paddle_side, new_y):
        """
        Update the paddle position for the specified side ('left' or 'right') to the new Y coordinate,
        ensuring it remains within the game bounds and does not exceed the paddle speed limit.
        """
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        paddle_key = "lp_y" if paddle_side == "left" else "rp_y"
        
        # Fetch the current Y position from Redis
        current_y = await self.redis.hget(dynamic_data_key, paddle_key)
        # print(f"fetched {paddle_side} paddle position from redis Redis: {current_y}")

        current_y = int(current_y) if current_y is not None else 0
        
        # Clamp the new Y position within the 0 to game_height range
        new_y = max(0, min(new_y, SCREEN_HEIGHT- PADDLE_HEIGHT))
        
        # Calculate the difference between the new and current position
        y_diff = abs(new_y - current_y)
        
        # Ensure the paddle does not move more than the paddle speed limit
        if y_diff <= PADDLE_SPEED:
            await self.redis.hset(dynamic_data_key, paddle_key, int(new_y))
            current_y = await self.redis.hget(dynamic_data_key, paddle_key)
        else:
            print(f"Attempted to move the {paddle_side} paddle more than the speed limit.")

    # ----------------------------REDIS TO CLIENT-----------------------------------

    async def update_redis_game_status(self, new_status: GameStatus):
        self.game_status = new_status
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        await self.redis.hset(dynamic_data_key, "gs", int(self.game_status.value))

        await self.send_redis_game_status_to_client()

    async def fetch_redis_game_status(self):
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        game_status = await self.redis.hget(dynamic_data_key, "gs")

        # print("CONSUMER --> game status: ", self.game_status)
        if game_status is not None:
            self.game_status = GameStatus(int(game_status))
            # print("EXIT")

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

    # -------------------------------GAME LOOP-----------------------------------

    # async def game_loop(self):
    #     last_update_time = time.time()
    #     print("CONSUMER -> LOOP STARTED for client : ", self.user_id)

    #     while True:
    #         # print("Game loop ongoing")
    #         current_time = time.time()
    #         delta_time = current_time - last_update_time

    #         # await self.send_redis_dynamic_data_to_client()

    #         target_fps = 60
    #         target_frame_time = 1.0 / target_fps
    #         sleep_duration = max(0, target_frame_time - delta_time)

    #         # Adjust the sleep duration based on the delta time
    #         await asyncio.sleep(sleep_duration)

    #         last_update_time = current_time

    #         await self.fetch_redis_game_status()

    #         if self.game_status != GameStatus.IN_PROGRESS:
    #             print("CONSUMER -> LOOP EXITED for client : ", self.user_id)
    #             break


    # -------------------------------CHANNEL LAYER-----------------------------------

    # async def game_init(self, event):
    #     message = event["message"]
    #     await self.send(text_data=json.dumps(message))

    # async def game_update(self, event):
    #     message = event["message"]
    #     await self.send(text_data=json.dumps(message))

    # async def start_game(self, event):
    #     await self.send(text_data=json.dumps({"type": "start_game"}))

    # async def broadcast_message(self, event):
    #     # Send message to WebSocket
    #     await self.send(text_data=json.dumps(event["message"]))

    async def game_static_data(self, event):
        # Logic to handle static data message
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'game.static_data',
            'data': data
        }))
        
    async def game_dynamic_data(self, event):
        # Logic to handle dynamic data message
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'game.dynamic_data',
            'data': data
        }))

    # # Add this method to your GameConsumer class
    # async def send_start_game_message(self, event):
    #     # Prepare the message in the format expected by the frontend
    #     message = {
    #         "type": "start_game",
    #         "message": "ready_to_play"
    #     }
    #     # Send the message to WebSocket
    #     await self.send(text_data=json.dumps(message))


    async def game_score_update(self, event):
        """
        Handle score update messages.
        """
        # Extract the relevant data from the event
        player_side = event['side']
        score = event['score']

        # Prepare the message to send to the client
        message = {
            'type': 'game.score_update',  # Confirming the message type
            'side': player_side,  # Indicating which player's score is updated
            'score': score  # The updated score
        }

        # Send the score update message to the client
        await self.send(text_data=json.dumps(message))

    async def game_status_update(self, event):
        """
        Handle receiving a game status update from the game logic.
        """
        # Extract the status from the event
        game_status = event['status']
        
        # Send the status to the WebSocket client
        await self.send(text_data=json.dumps({
            'type': 'game.status_update',
            'status': game_status
        }))