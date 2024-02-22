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
        
        # Fetch the number of connected clients by checking the set's cardinality
        connected_clients = await self.redis.scard(connected_clients_set_key)

        print("CONSUMER -> check connected : ", self.user_id)
        print("CONSUMER -> nb connected : ", connected_clients)

        await self.attempt_to_acquire_game_logic_control()

        if self.handle_game_logic:
            self.game_logic_instance = GameLogic(self.room_name)
            self.game_logic_task = asyncio.create_task(self.game_logic_instance.run_game_loop())

    async def disconnect(self, close_code):
        print(f"CONSUMER -> DISCONNECT for client: {self.user_id}")
        if self.handle_game_logic:
            await self.redis.delete("game_logic_flag")
        
        if hasattr(self, 'game_logic_task') and not self.game_logic_task.done():
            self.game_logic_task.cancel()
            try:
                # Wait for the task to be cancelled
                # This ensures any cleanup within the task can complete
                await self.game_logic_task
            except asyncio.CancelledError:
                # The task was cancelled, so any necessary cleanup should be done here
                print(f"Game logic task for {self.user_id} was cancelled.")

        # Cancel game_loop_task if it exists and is not done
        if hasattr(self, 'game_loop_task') and not self.game_loop_task.done():
            self.game_loop_task.cancel()
            try:
                await self.game_loop_task
            except asyncio.CancelledError:
                print(f"Game loop task for {self.user_id} was cancelled.")

            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Remove this user from the set of connected users
        connected_users_set_key = f"game:{self.room_name}:connected_users"
        await self.redis.srem(connected_users_set_key, self.user_id)

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Handle "ready_to_play" message
        if "message" in data and data["message"] == "ready_to_play":
            print("Player is ready to play : ", self.user_id)
            self.game_loop_task = asyncio.create_task(self.game_loop())


        # Handle "paddle_position_update" message
        elif "type" in data and data["type"] == "paddle_position_update":
            paddle_y = data.get('PaddleY')
            if paddle_y is not None:
                print(f"Received paddle position update: {paddle_y}")
                # Update game logic with new paddle position
                if hasattr(self, 'game_logic_instance'):
                    await self.game_logic_instance.update_paddle_position('left', paddle_y)
                else:
                    print("Game logic instance not found or not initialized")
        else:
            print("Received unknown message type or missing key.")


    async def attempt_to_acquire_game_logic_control(self):
        # Attempt to set the flag indicating this consumer should handle the game logic
        flag_set = await self.redis.setnx("game_logic_flag", "true")
        if flag_set:
            # This consumer will handle the game logic
            self.handle_game_logic = True
            # Set an expiration time for the flag to avoid stale locks
            await self.redis.expire("game_logic_flag", 60)  # Expires in 60 seconds
        else:
            self.handle_game_logic = False




    # ----------------------------REDIS TO CLIENT-----------------------------------

    # async def send_redis_static_data_to_client(self):
    #     static_data_key = f"game:{self.room_name}:static"
    #     static_data = await self.redis.hgetall(static_data_key)

    #     # print(f"Sending static game data to client: {static_data}")
        
    #     static_data_str = json.dumps({"type": "game.static_data", "data": static_data})
    #     await self.send(text_data=static_data_str)

    #     # Directly send the static game data to the frontend
    #     # Note: The client will need to handle any necessary data parsing
    #     # await self.channel_layer.group_send(
    #     #     self.room_group_name, 
    #     #     {
    #     #         "type": "game.static_data", 
    #     #         "data": static_data  # Sending the Redis hash map as is
    #     #     }
    #     # )

    # async def send_redis_dynamic_data_to_client(self):
    #     dynamic_data_key = f"game:{self.room_name}:dynamic"
    #     dynamic_data = await self.redis.hgetall(dynamic_data_key)

    #     print(f"Sending dynamic game data to client: {dynamic_data}")
        
    #     dynamic_data_str = json.dumps({"type": "game.dynamic_data", "data": dynamic_data})
    #     await self.send(text_data=dynamic_data_str)

    #     # Directly send the dynamic game data to the frontend
    #     # Note: The client will need to handle deserialization of JSON fields
    #     # await self.channel_layer.group_send(
    #     #     self.room_group_name, 
    #     #     {
    #     #         "type": "game.dynamic_data", 
    #     #         "data": dynamic_data  # Sending the Redis hash map as is
    #     #     }
    #     # )

    async def fetch_redis_game_status(self):
        dynamic_data_key = f"game:{self.room_name}:dynamic"
        game_status = await self.redis.hget(dynamic_data_key, "gs")

        # print("CONSUMER --> game status: ", self.game_status)
        if game_status is not None:
            self.game_status = GameStatus(int(game_status))
            # print("EXIT")

    # -------------------------------GAME LOOP-----------------------------------

    async def game_loop(self):
        last_update_time = time.time()
        print("CONSUMER -> LOOP STARTED for client : ", self.user_id)

        while True:
            # print("Game loop ongoing")
            current_time = time.time()
            delta_time = current_time - last_update_time

            # await self.send_redis_dynamic_data_to_client()

            target_fps = 60
            target_frame_time = 1.0 / target_fps
            sleep_duration = max(0, target_frame_time - delta_time)

            # Adjust the sleep duration based on the delta time
            await asyncio.sleep(sleep_duration)

            last_update_time = current_time

            await self.fetch_redis_game_status()

            if self.game_status != GameStatus.IN_PROGRESS:
                print("CONSUMER -> LOOP EXITED for client : ", self.user_id)
                break


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

    # Add this method to your GameConsumer class
    async def send_start_game_message(self, event):
        # Prepare the message in the format expected by the frontend
        message = {
            "type": "start_game",
            "message": "ready_to_play"
        }
        # Send the message to WebSocket
        await self.send(text_data=json.dumps(message))
