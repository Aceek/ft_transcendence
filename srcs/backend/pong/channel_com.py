import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ChannelCom:
    def __init__(self, room_name):
        self.room_name = room_name
        self.room_group_name = f'game_{room_name}'  # Adjust naming convention as needed
        self.channel_layer = get_channel_layer()

    async def send_static_data(self, static_data):
        message = {
            "type": "game.static_data",
            "data": static_data
        }
        await self.channel_layer.group_send(self.room_group_name, message)

    async def send_dynamic_data(self, dynamic_data):
        message = {
            "type": "game.dynamic_data",
            "data": dynamic_data
        }
        await self.channel_layer.group_send(self.room_group_name, message)
        
    async def send_game_status(self, game_status):
        message = {
            "type": "game.status_update",
            "status": game_status
        }
        await self.channel_layer.group_send(self.room_group_name, message)

    async def send_paddle_assignment(self, user_id, paddle_side):
        message = json.dumps({
            'type': 'game.paddle_side',
            'paddle_side': paddle_side
        })
        # Assuming user_id can be mapped to a specific channel name or user-specific group
        await self.channel_layer.send(user_id, message)

