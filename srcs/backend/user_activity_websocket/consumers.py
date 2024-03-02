import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import asyncio
from datetime import datetime
import aioredis



class UserActivityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.send_error("You are not authenticated")
            await self.close()
            return
        self.user_id = str(self.user.id)
        self.user_activity_group_name = f"user_activity_{self.user_id}"
        await self.channel_layer.group_add(
            self.user_activity_group_name, self.channel_name
        )
        await self.send(text_data=json.dumps({"status": "connected"}))
        self.redis = await aioredis.from_url("redis://redis:6379", db=0)

        await self.mark_online()

        await self.increment_connection_count()

        self.last_ping = datetime.now()

        asyncio.create_task(self.check_heartbeats())

    @database_sync_to_async
    def mark_online(self):
        self.user.status = "online"
        self.user.save()

    @database_sync_to_async
    def mark_offline(self):
        self.user.status = "offline"
        self.user.save()

    async def disconnect(self, close_code):
        await self.decrement_connection_count()
        connection_left = await self.get_connection_count()
        if connection_left <= 0:
            await self.mark_offline()
            await self.channel_layer.group_discard(
                self.user_activity_group_name, self.channel_name
            )
        await self.redis.close()
        await self.redis.wait_closed()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        if action == "ping":
            self.last_ping = datetime.now()
            await self.send(text_data=json.dumps({"status": "pong"}))
        else:
            await self.send_error("Invalid action")

    async def send_error(self, error_message):
        await self.send(text_data=json.dumps({"error": error_message}))

    async def check_heartbeats(self):
        while True:
            await asyncio.sleep(30)
            now = datetime.now()
            if (now - self.last_ping).total_seconds() > 60:
                await self.mark_offline()
                break

    async def increment_connection_count(self):
        await self.redis.incr(f"user_{self.user_id}_connections")

    async def decrement_connection_count(self):
        await self.redis.decr(f"user_{self.user_id}_connections")

    async def get_connection_count(self):
        return int(await self.redis.get(f"user_{self.user_id}_connections") or 0)
