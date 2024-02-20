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
            game_logic_instance = GameLogic(self.room_name)
            asyncio.create_task(game_logic_instance.run_game_loop())

        # Fetch game initialization data from Redis
        await self.send_redis_static_data_to_client()
        await self.send_redis_dynamic_data_to_client()

        await self.accept()

        # await self.channel_layer.group_send(
        #     self.room_group_name, {"type": "game_init", "message": game_init_data}
        # )

        #  send message to verify the connection and player is ready to play
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "start_game"}
        )

        async def disconnect(self, close_code):
            # Change game status to paused
            print("disconnected")
            # self.game_status = "paused"
            await self.redis.hset(f"game_state:{self.room_name}", "status", "paused")
            
            # # Broadcast the game pause to all clients
            # pause_message = {
            #     "type": "broadcast_message",
            #     "message": {
            #         "type": "game.paused",
            #         "data": {"reason": "Player disconnected", "gameStatus": self.game_status},
            #     },
            # }
            # await self.channel_layer.group_send(self.room_group_name, pause_message)
            
            # Remove this channel from the group
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            
            if self.handle_game_logic:
                # Clear the flag as this consumer was responsible for the game logic
                await self.redis.delete("game_logic_flag")

            # Optionally, reset the game or handle the disconnection further
            # self.initialize_game()  # Consider when and how to reset game state


        async def receive(self, text_data):
            data = json.loads(text_data)

            delta_time = 0.0

            if data["message"] == "ready_to_play":
                self.ready_to_play += 1
                print("Player is ready to play")
                if self.ready_to_play == 2:
                    print("Both players are ready to play")
                    # self.ball_launched = True
                    # self.game_status = "ongoing"
                    asyncio.create_task(self.game_loop())
            # if data["message"] == "paddle_movement":
            #     await self.handle_paddle_movement(data, delta_time)
            # else:
            #     await self.handle_game_update(delta_time, data)

    # ----------------------------REDIS TO CLIENT-----------------------------------

    async def send_redis_static_data_to_client(self):
        static_data_key = f"game:{self.room_name}:static"
        static_data = await self.redis.hgetall(static_data_key)

        print(f"Sending static game data to client: {static_data}")

        # Directly send the static game data to the frontend
        # Note: The client will need to handle any necessary data parsing
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

        print(f"Sending dynamic game data to client: {dynamic_data}")

        # Directly send the dynamic game data to the frontend
        # Note: The client will need to handle deserialization of JSON fields
        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                "type": "game.dynamic_data", 
                "data": dynamic_data  # Sending the Redis hash map as is
            }
        )

    # -------------------------------GAME LOOP-----------------------------------

    async def game_loop(self):
        last_update_time = time.time()
        print("Game loop started")

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

