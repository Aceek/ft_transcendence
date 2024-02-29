import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

from .paddle import Paddle
from .connect_utils import *
from ..game.config import *
from ..game.player import Player
from ..game.channel_com import ChannelCom
from ..game.game import GameLogic
from ..game.enum import GameStatus
from ..redis.redis_ops import RedisOps

class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # -------------------------------CONNECT-----------------------------------

    async def connect(self):
        # Accept the incoming connection
        await self.accept()
        
        # Retrieve and set the user's ID and room names based on the connection's scope
        self.user_id = get_user_id(self.scope)
        self.room_name, self.room_group_name = get_room_names(self.scope)

        # Add this channel to the group and instanciate the Channel commmunication class
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.channel_com = ChannelCom(self.room_group_name)
        
        # Initialize Redis operations helper for the room and add the user as connected
        self.redis_ops = await RedisOps.create(self.room_name)
        await self.redis_ops.add_connected_users(self.user_id)
        
        # Create a Paddle object for the user, assign it, and notify the client of their paddle side
        self.paddle = Paddle(self.user_id, self.redis_ops)
        await self.paddle.assignment()
        await self.send_client_paddle_side()

        # Check if the client is the first to connect to the room; 
        # if so, client acquire the game logic flag and start game logic in a new task
        if await self.redis_ops.get_game_status() is None:
            if await self.redis_ops.add_game_logic_flag():
                asyncio.create_task(GameLogic(self.room_name, self.room_group_name).run())
        else:
            # Retrieve data from the existing game
            static_data = await self.redis_ops.get_static_data()
            await self.channel_com.send_static_data(static_data)

            dynamic_data = await self.redis_ops.get_dynamic_data()
            await self.channel_com.send_dynamic_data(dynamic_data)

            # print
    # -------------------------------DISCONNECT-----------------------------------
                
    async def disconnect(self, close_code):
        
        # If the game is in progress, set its status to suspended
        current_status = await self.redis_ops.get_game_status()
        if current_status == GameStatus.IN_PROGRESS:
            await self.redis_ops.set_game_status(GameStatus.SUSPENDED)

        # Remove this user from the list of connected users and delete any restart request from them
        await self.redis_ops.del_connected_user(self.user_id)
        await self.redis_ops.del_restart_request(self.user_id)

        # If no users are connected anymore, clear all data related to this room
        if await self.redis_ops.get_connected_users() == 0:
            await self.redis_ops.clear_all_data()
        
        # Remove this channel from the group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # -------------------------------RECEIVE-----------------------------------
        
    async def receive(self, text_data):
        data = json.loads(text_data)

        # Handle "paddle_position_update" message
        if "type" in data and data["type"] == "paddle_position_update":
            paddle_y = data.get('PaddleY')
            if paddle_y is not None and self.paddle.side is not None:
                if await self.paddle.check_movement(paddle_y):
                    await self.paddle.set_data_to_redis(paddle_y)

        # Handle "restart_game" message
        elif "type" in data and data["type"] == "restart_game":
            await self.redis_ops.add_restart_requests(self.user_id)
        else:
            print("Received unknown message type or missing key.")
    
    # ----------------------------SEND-------------------------------------

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

    async def game_countdown(self, event):
        seconds = event['seconds']
        await self.send(text_data=json.dumps({
            'type': 'game.countdown',
            'seconds': seconds
        }))

    async def send_client_paddle_side(self):
        if self.paddle.side is not None:
            await self.send(text_data=json.dumps({
                'type': 'game.paddle_side',
                'paddle_side': self.paddle.side.name,
            }))
        else:
            print(f"No paddle side assigned for user: {self.user_id}")