from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ChannelCom:
    def __init__(self, room_name):
        self.room_name = room_name
        self.room_group_name = f'pong_room_{room_name}'
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

