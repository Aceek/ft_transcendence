import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

from .paddle import Paddle
from .connect_utils import *
from ..game.utils import get_player_key_map
from ..game.channel_com import ChannelCom
from ..game.game import GameLogic
from ..game.enum import GameStatus
from ..redis.redis_ops import RedisOps
from ..database.database_ops import DatabaseOps

class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assigned = False

    # -------------------------------CONNECT-----------------------------------

    async def connect(self):
        # Accept the incoming connection
        await self.accept()
        
        # Retrieve game infos based on the connection's scope
        self.user_id = get_user_id(self.scope)
        self.username = get_username(self.scope)
        self.game_mode = get_game_mode(self.scope)
        self.player_nb = get_number_of_players(self.scope)
        self.game_type = get_game_type(self.scope)
        self.room_name, self.room_group_name = get_room_names(self.scope)

        # Add this channel to the group and instanciate the Channel commmunication class
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.channel_com = ChannelCom(self.room_group_name)
        
        # Initialize Redis and Databse operations helper for the room
        self.redis_ops = await RedisOps.create(self.room_name)
        self.database_ops = DatabaseOps()

        # Create a Paddle object for the user, assign it, and notify the client of their paddle side
        self.paddle = Paddle(self.user_id, self.redis_ops, self.player_nb)
        self.assigned = await self.paddle.assignment(self.player_nb)
        if self.assigned == True:
            await self.paddle.set_boundaries()
            await self.paddle.set_axis_keys()
        await self.send_paddle_assignement()

        # Once paddle has been assigned, notify the server that the player is assigned and ready to play
        if self.assigned == True:
            await self.redis_ops.add_connected_users(self.user_id)
            await self.database_ops.set_user_status(self.user_id, "in-game")
        else:
            await self.database_ops.set_user_status(self.user_id, "spectacting")

        # Check if the client is the first to connect to the room; 
        # if so, client acquire the game logic flag and start game logic in a new task
        current_status = await self.redis_ops.get_game_status()
        if current_status is None and self.assigned == True:
            if await self.redis_ops.add_game_logic_flag():
                self.task = asyncio.create_task(GameLogic(self).run())
        else:
            # Retrieve and send data from the existing game
            await self.send_game_data(current_status)

    # -------------------------------DISCONNECT-----------------------------------
                
    async def disconnect(self, close_code):
        
        if self.assigned:
            # If the game is in progress, set its status to suspended
            current_status = await self.redis_ops.get_game_status()
            if current_status != GameStatus.COMPLETED:
                await self.redis_ops.set_game_status(GameStatus.SUSPENDED)

            # Remove this user from the list of connected users and delete any restart request from them
            await self.redis_ops.del_connected_user(self.user_id)
            await self.redis_ops.del_restart_request(self.user_id)
            # Potentially not online anymore -> to be tested
        await self.database_ops.set_user_status(self.user_id, "online")
        
        # # Remove this channel from the group
        # await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # -------------------------------RECEIVE-----------------------------------
        
    async def receive(self, text_data):
        data = json.loads(text_data)

        # Handle "paddle_position_update" message
        if "type" in data and data["type"] == "update":
            pos = data.get('pos')
            if pos is not None and self.paddle.side is not None:
                if await self.paddle.check_movement(pos):
                    await self.paddle.set_data_to_redis(pos)
        # Handle "restart_game" message
        elif "type" in data and data["type"] == "restart_game":
            await self.redis_ops.add_restart_requests(self.user_id)
        # Handling different types of messages
        elif "type" in data and data["type"] == "ping":
            await self.send_pong(data)
        else:
            print("Received unknown message type or missing key.")
    
    # ----------------------------SEND-------------------------------------

    async def game_static_data(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'game.static_data',
            'data': data
        }))
        
    async def game_dynamic_data(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'game.dynamic_data',
            'data': data,
        }))

    async def game_compacted_dynamic_data(self, event):
        ball_data = event['ball']
        player_data = event['players']
        
        await self.send(text_data=json.dumps({
            'type': 'game.compacted_dynamic_data',
            'ball': ball_data,
            'players': player_data,
        }))

    async def game_countdown(self, event):
        seconds = event['seconds']
        await self.send(text_data=json.dumps({
            'type': 'game.countdown',
            'seconds': seconds
        }))

    async def send_paddle_assignement(self):
        if self.paddle.side is not None:

            key_map = get_player_key_map(self.paddle.side)
            await self.send(text_data=json.dumps({
                'type': 'game.paddle_side',
                'paddle_side': key_map['position'],
            }))
            print(f"paddle side {key_map['position']} assigned for user: {self.user_id}")
        else:
            print(f"No paddle side assigned for user: {self.user_id}")

    async def send_game_data(self, current_status):
        if current_status is not None:
            static_data = await self.redis_ops.get_static_data()
            static_event = {'data': static_data}
            await self.game_static_data(static_event)

        if current_status != GameStatus.UNSTARTED:
            dynamic_data = await self.redis_ops.get_dynamic_data()
            dynamic_event = {'data': dynamic_data}
            await self.game_dynamic_data(dynamic_event)

    async def send_pong(self, data):
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': data['timestamp']
        }))
