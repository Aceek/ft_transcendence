from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid
import aioredis
from channels.layers import get_channel_layer


class MatchmakingConsumer(AsyncWebsocketConsumer):
    user_mode = None

    async def connect(self):
        await self.accept()
        if self.scope["user"].is_anonymous:
            await self.send_error("You are not authenticated")
            await self.close()
            return
        self.user_id = str(self.scope["user"].id)
        self.redis = await aioredis.from_url("redis://redis:6379", db=0)
        await self.redis.set(f"user_{self.user_id}_ws_channel", self.channel_name)

        self.mark_for_remove = False

    async def receive(self, text_data):
        data = json.loads(text_data)
        mode = data.get("mode")
        if data["action"] == "startMatchmaking" and mode:
            await self.start_matchmaking(mode)

    async def start_matchmaking(self, mode):
        user_in_any_queue = await self.redis.sismember(
            "global_matchmaking_queue", self.user_id
        )
        if user_in_any_queue:
            await self.send_error("You are already in a queue")
            await self.close()
            return

        added_to_global_queue = await self.redis.sadd(
            "global_matchmaking_queue", self.user_id
        )

        if not added_to_global_queue:
            await self.send_error("You are already in a queue")
            await self.close()
            return

        queue_name = f"matchmaking_queue_{mode}"
        await self.redis.lpush(queue_name, self.user_id)
        await self.redis.set(f"user_{self.user_id}_mode", mode)

        self.user_mode = mode
        self.mark_for_remove = True

        await self.check_for_match(queue_name, mode)

    async def check_for_match(self, queue_name, mode):
        required_players = int(mode[0])
        queue_length = await self.redis.llen(queue_name)
        if queue_length >= required_players:
            player_ids = [
                await self.redis.rpop(queue_name) for _ in range(required_players)
            ]
            player_ids = [pid.decode("utf-8") for pid in player_ids if pid]
            if len(player_ids) == required_players:
                room_id = str(uuid.uuid4())
                room_url = f"/pong/{room_id}"
                await self.notify_players_about_match(player_ids, room_url)
                for pid in player_ids:
                    await self.redis.srem("global_matchmaking_queue", pid)
                    await self.redis.delete(f"user_{pid}_ws_channel")

    async def notify_players_about_match(self, player_ids, room_url):
        channel_layer = get_channel_layer()
        for player_id in player_ids:
            player_channel = await self.redis.get(f"user_{player_id}_ws_channel")
            if player_channel:
                await channel_layer.send(
                    player_channel.decode("utf-8"),
                    {
                        "type": "send_message",
                        "text": json.dumps(
                            {
                                "message": "Match found",
                                "room_url": room_url,
                            }
                        ),
                    },
                )

    async def send_message(self, event):
        await self.send(text_data=event["text"])

    async def disconnect(self, close_code):
        if self.mark_for_remove:
            user_mode = await self.redis.get(f"user_{self.user_id}_mode")
            if user_mode:
                user_mode = user_mode.decode("utf-8")
                queue_name = f"matchmaking_queue_{user_mode}"
                await self.redis.lrem(queue_name, 0, self.user_id)

            await self.redis.srem("global_matchmaking_queue", self.user_id)
            await self.redis.delete(f"user_{self.user_id}_mode")
            await self.redis.delete(f"user_{self.user_id}_ws_channel")

        await self.redis.close()

    async def send_error(self, message):
        await self.send(text_data=json.dumps({"error": True, "message": message}))
