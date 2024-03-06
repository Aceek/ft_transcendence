import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import asyncio
from datetime import datetime
import aioredis
import time
from datetime import timedelta
import uuid


class UserActivityConsumer(AsyncWebsocketConsumer):
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
        await self.send(text_data=json.dumps({"error": error_message}))

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

    async def send_challenge_user(self, challenged_id):
        challegend_id_online = await self.isUserOnline(challenged_id)
        challenged_channel = f"user_communication_{challenged_id}"
        if challegend_id_online:
            await self.channel_layer.group_send(
                challenged_channel,
                {
                    "type": "challenge_user",
                    "action": "challenge_received",
                    "challenger_id": self.user_id,
                },
            )
        else:
            await self.send_error_challenge(challenged_id, "User is not available")

    async def challenge_user(self, event):
        challenger_id = event["challenger_id"]

        message = {"action": "challenge_received", "challenger_id": challenger_id}

        await self.send(text_data=json.dumps(message))

    async def send_error_challenge(self, challenged_id, message):
        await self.send(
            text_data=json.dumps(
                {
                    "action": "challenge_error",
                    "message": challenged_id + ": " + message,
                }
            )
        )

    @database_sync_to_async
    def isUserOnline(self, user_id):
        from CustomUser.models import CustomUser

        user = CustomUser.objects.get(id=user_id)
        return user.status == "online"

    async def challenge_received(self, challenger_id):
        await self.send(
            text_data=json.dumps(
                {
                    "action": "challenge_received",
                    "challenger_id": challenger_id,
                }
            )
        )

    async def send_challenge_response_to_self(self, response, room_url):
        await self.send(
            text_data=json.dumps(
                {
                    "action": "challenge_response",
                    "response": response,
                    "challenger_id": self.user_id,
                    "room_url": room_url,
                }
            )
        )

    def create_room_url(self):
        room_id = str(uuid.uuid4())
        return f"/pong/{room_id}"

    async def send_challenge_response(self, challenger_id, response):
        challenger_channel = f"user_communication_{challenger_id}"
        is_challegend_online = await self.isUserOnline(challenger_id)
        room_url = self.create_room_url()
        if is_challegend_online:
            await self.channel_layer.group_send(
                challenger_channel,
                {
                    "type": "challenge_response",
                    "challenger_id": self.user_id,
                    "action": "challenge_response",
                    "response": response,
                    "room_url": room_url,
                },
            )
            await self.send_challenge_response_to_self(response, room_url)
        else:
            await self.send_error_challenge(challenger_id, "User is not available")

    async def challenge_response(self, event):
        response = event["response"]
        challenger_id = event["challenger_id"]
        room_url = event["room_url"]
        await self.send(
            text_data=json.dumps(
                {
                    "action": "challenge_response",
                    "response": response,
                    "challenger_id": challenger_id,
                    "room_url": room_url,
                }
            )
        )

    async def send_cancel_challenge(self, challenged_id):
        challenged_channel = f"user_communication_{challenged_id}"
        is_challegend_online = await self.isUserOnline(challenged_id)
        if is_challegend_online:
            await self.channel_layer.group_send(
                challenged_channel,
                {
                    "type": "cancel_challenge",
                    "action": "cancel_challenge",
                    "challenger_id": self.user_id,
                },
            )
        else:
            await self.send_error_challenge(challenged_id, "User is not available")

    async def cancel_challenge(self, event):
        challenger_id = event["challenger_id"]
        await self.send(
            text_data=json.dumps(
                {
                    "action": "cancel_challenge",
                    "challenger_id": challenger_id,
                }
            )
        )
