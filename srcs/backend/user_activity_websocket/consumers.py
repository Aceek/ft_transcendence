import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import asyncio
from datetime import datetime
import aioredis
import time
from datetime import timedelta
import uuid
from .challenge_user import ChallengeUserMixin


class UserActivityConsumer(AsyncWebsocketConsumer, ChallengeUserMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connected = True

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

        self.communication_group_name = f"user_communication_{self.user_id}"
        await self.channel_layer.group_add(
            self.communication_group_name, self.channel_name
        )

        self.redis = await aioredis.from_url("redis://redis:6379", db=0)

        await self.mark_online()

        self.last_ping = datetime.now()

        asyncio.create_task(self.check_inactivity())

    @database_sync_to_async
    def mark_online(self):
        if self.user.status != "online":
            self.user.status = "online"
            self.user.save()

    async def mark_user_offline(self):
        await self.redis.delete(f"user_last_ping:{self.user_id}")
        await self.mark_offline()

    @database_sync_to_async
    def mark_offline(self):
        self.user.status = "offline"
        self.user.save()

    async def disconnect(self, close_code):
        if hasattr(self, "user_activity_group_name"):
            await self.channel_layer.group_discard(
                self.user_activity_group_name, self.channel_name
            )
        if hasattr(self, "communication_group_name"):
            await self.channel_layer.group_discard(
                self.communication_group_name, self.channel_name
            )
        self.connected = False

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        if action == "ping":
            await self.handle_ping()
            await self.send(text_data=json.dumps({"action": "pong"}))
        elif action == "track_status":
            await self.track_status_and_send(data["user_ids"])
        elif action == "challenge_received":
            challenger_id = data["challenger_id"]
            await self.challenge_received(challenger_id)
        elif action == "challenge_response":
            challenger_id = data["challenger_id"]
            response = data["response"]
            await self.send_challenge_response(challenger_id, response)
        elif action == "challenge_user":
            challenged_id = data["challenged_id"]
            await self.send_challenge_user(challenged_id)
        elif action == "cancel_challenge":
            challenged_id = data["challenged_id"]
            await self.send_cancel_challenge(challenged_id)

    async def send_error(self, error_message):
        await self.send(text_data=json.dumps({"error": "anonymous_user", "message": error_message}))

    async def handle_ping(self):
        self.last_ping = datetime.now()
        current_timestamp = int(time.time())
        await self.redis.set(f"user_last_ping:{self.user_id}", current_timestamp)

    async def check_inactivity(self):
        await self.redis.incr(f"user:{self.user_id}:inactivity_checks")

        async def check_and_mark_offline():
            last_ping_timestamp = await self.redis.get(f"user_last_ping:{self.user_id}")
            if last_ping_timestamp:
                last_ping = int(last_ping_timestamp)
                current_timestamp = int(time.monotonic())
                if current_timestamp - last_ping > 60:
                    await self.mark_user_offline()
                else:
                    await self.mark_online()

        try:
            while self.connected:
                await asyncio.sleep(20)
                await check_and_mark_offline()
        finally:
            checks_left = await self.redis.decr(
                f"user:{self.user_id}:inactivity_checks"
            )
            if checks_left <= 0:
                await self.mark_user_offline()
                await self.redis.delete(f"user:{self.user_id}:inactivity_checks")

    async def track_status_and_send(self, user_ids):
        await self.track_status(user_ids)
        for user_id in user_ids:
            user = await self.get_user(user_id)
            await self.send(
                text_data=json.dumps(
                    {
                        "action": "status_update",
                        "status": user.status,
                        "user_id": str(user.id),
                    }
                )
            )

    @database_sync_to_async
    def get_user(self, user_id):
        from CustomUser.models import CustomUser

        return CustomUser.objects.get(id=user_id)

    async def track_status(self, user_ids):
        for user_id in user_ids:
            await self.channel_layer.group_add(
                f"user_activity_{user_id}", self.channel_name
            )

    async def user_activity(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "action": event["action"],
                    "status": event["status"],
                    "user_id": event["user_id"],
                }
            )
        )

  