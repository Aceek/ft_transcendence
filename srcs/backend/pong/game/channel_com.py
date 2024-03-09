from datetime import datetime

from channels.layers import get_channel_layer

class ChannelCom:
    def __init__(self, room_group_name):
        self.room_group_name = room_group_name
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
            "data": dynamic_data,
        }
        await self.channel_layer.group_send(self.room_group_name, message)

    async def send_compacted_dynamic_data(self, ball_data, player_data):
        current_time_ms = int(datetime.now().timestamp() * 1000)

        message = {
            "type": "game.compacted_dynamic_data",
            "ball": ball_data,
            "players": player_data,
            "time": current_time_ms,
        }
        await self.channel_layer.group_send(self.room_group_name, message)

    async def send_countdown(self, seconds_left):
        message = {
            "type": "game.countdown",
            "seconds": seconds_left
        }
        await self.channel_layer.group_send(self.room_group_name, message)

