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
from .redis_ops import RedisOps

class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.paddle_side = None

    # -------------------------------WEBSOCKET-------------------------

    async def connect(self):
        await self.accept()
        self.user_id = self.get_user_id()
        self.room_name, self.room_group_name = self.get_room_names()
        print("CONSUMER -> client connected : ", self.user_id)

        # Initialize Redis operations
        self.redis_ops = await RedisOps.create(self.room_name)

        # Join the game room group and assign paddle
        await self.join_room_group()
        await self.handle_paddle_assignment()

        # Check the current game status
        await self.start_game_logic_task()

    def get_user_id(self):
        """Determine the user ID based on authentication status."""
        return str(self.scope["user"].id if self.scope["user"].is_authenticated else "anonymous")

    def get_room_names(self):
        """Generate room and group names based on the game UID."""
        room_name = self.scope["url_route"]["kwargs"]["uid"]
        room_group_name = f"pong_room_{room_name}"
        return room_name, room_group_name

    async def join_room_group(self):
        """Add the user to the room group in Channels and Redis."""
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.redis_ops.add_connected_users(self.room_name, self.user_id)

    async def handle_paddle_assignment(self):
        # Keys for each paddle position
        positions = ['left', 'right']
        paddle_position_keys = {pos: f"game:{self.room_name}:paddle:{pos}" for pos in positions}

        # Check if the player already has an assigned position
        for position, key in paddle_position_keys.items():
            if await self.redis_ops.connection.sismember(key, self.user_id):
                self.paddle_side = position
                break
        else:
            # Assign the player to the next available position
            for position, key in paddle_position_keys.items():
                if not await self.redis_ops.connection.scard(key):
                    await self.redis_ops.connection.sadd(key, self.user_id)
                    self.paddle_side = position
                    break

        await self.send_paddle_side_assignment()
        print(f"User {self.user_id} assigned to {self.paddle_side} paddle")

    async def attempt_to_acquire_game_logic_control(self):
        print(f"Attempting to start game logic: {self.user_id}, Time: {time.time()}")
        flag_key = f"game:{self.room_name}:logic_flag"  # Updated to match the new pattern
        flag_set = await self.redis_ops.connection.setnx(flag_key, "true")
        if flag_set:
            print("CONSUMER -> client set the flag : ", self.user_id)
            await self.redis_ops.connection.expire(flag_key, 60)
            return True
        return False

    async def start_game_logic_task(self):
        """Check the current game status and initiate game logic if necessary."""
        current_status = await self.redis_ops.get_game_status(self.room_name)
        if current_status is None:
            if await self.attempt_to_acquire_game_logic_control():
                asyncio.create_task(GameLogic(self.room_name).run())
                print("CONSUMER -> client started game logic : ", self.user_id)

    async def disconnect(self, close_code):
        
        current_status = await self.redis_ops.get_game_status(self.room_name)
        if current_status != GameStatus.COMPLETED:
            await self.redis_ops.set_game_status(self.room_name, GameStatus.SUSPENDED)

        await self.redis_ops.del_connected_users(self.room_name, self.user_id)
        await self.redis_ops.del_restart_requests(self.room_name, self.user_id)

        if await self.redis_ops.get_connected_users(self.room_name) == 0:
            await self.redis_ops.clear_data(self.room_name)
        
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Handle "paddle_position_update" message
        if "type" in data and data["type"] == "paddle_position_update":
            paddle_y = data.get('PaddleY')
            if paddle_y is not None and self.paddle_side is not None:
                # Update game logic with new paddle position
                if await self.check_paddle_move(self.paddle_side, paddle_y):
                    await self.redis_ops.set_paddle(self.room_name, self.paddle_side, paddle_y)

        elif "type" in data and data["type"] == "restart_game":
            # Handle restart game request
            await self.redis_ops.add_restart_requests(self.room_name, self.user_id)
        else:
            print("Received unknown message type or missing key.")

    # -------------------------------CHECK-----------------------------------

    async def check_paddle_move(self, paddle_side, new_y):
        """
        Method to update the paddle position for the specified side ('left' or 'right')
        to the new Y coordinate, using the existing RedisOps functionality.
        """

        # Early checks for requested Y position out of bounds
        if new_y < 0:
            print(f"Requested paddle move for {paddle_side} is below 0. Clamping to 0.")
            return False
        elif new_y > SCREEN_HEIGHT - PADDLE_HEIGHT:
            print(f"Requested paddle move for {paddle_side} exceeds screen height. Clamping to {SCREEN_HEIGHT - PADDLE_HEIGHT}.")
            return False

        # Fetch the current Y position from Redis using the RedisOps class
        current_y = await self.redis_ops.get_dynamic_value(self.room_name, f"{paddle_side[0]}p_y")  # lp_y or rp_y based on paddle_side
        current_y = int(current_y) if current_y is not None else 0

        # Calculate the difference between the new and current position
        y_diff = abs(new_y - current_y)

        # Ensure the paddle does not move more than the paddle speed limit
        if y_diff <= PADDLE_SPEED:
            # Use the RedisOps method to update the paddle's position
            return True
        else:
            print(f"Attempted to move the {paddle_side} paddle more than the speed limit.")
            return False
    
    # ----------------------------CHANNEL SEND-----------------------------------

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
    
    async def send_paddle_side_assignment(self):
        """
        Sends a message to the connected client with their paddle side assignment.
        """
        if self.paddle_side:
            await self.send(text_data=json.dumps({
                'type': 'game.paddle_side',
                'paddle_side': self.paddle_side
            }))
        else:
            print(f"No paddle side assigned for user: {self.user_id}")

    # -------------------------------CHANNEL MESSAGE-------------------------------------

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