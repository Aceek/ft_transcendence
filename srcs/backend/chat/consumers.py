from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
import redis
from django.utils import timezone
import asyncio
from channels.exceptions import StopConsumer


# from CustomUser.models import CustomUser


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.followed_users = []
        self.pong_received = True
        self.active = True

    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.room_group_name = f"chat_{str(self.user.id)}"

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.mark_user_online(str(self.user.id))
            await self.accept()
            await self.send_unread_messages(str(self.user.id))
            await self.verify_active_tournament()
            await self.verify_active_match()
            asyncio.create_task(self.ping_client())

        else:
            await self.close()

    async def disconnect(self, close_code):
        self.active = False
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.mark_user_offline(str(self.user.id))

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        if action == "subscribe":
            await self.subscribe_to_status_updates(data["usersIds"])
        elif action == "send_message":
            message = data["message"]
            receiver_id = data.get("receiver")
            receiver_group_name = f"chat_{receiver_id}"
            if await self.can_send_message(receiver_id):
                await self.store_message(receiver_id, message)
                await self.channel_layer.group_send(
                    receiver_group_name,
                    {
                        "type": "chat_message",
                        "message": message,
                        "sender": str(self.user.id),
                        "receiver": receiver_id,
                    },
                )
        elif action == "get_status_updates":
            await self.send_status_updates()
        elif action == "pong":
            self.pong_received = True
        elif action == "read_messages":
            await self.mark_message_as_read(data["receiver"])


    @database_sync_to_async
    def get_unread_messages(self, user_id):
        from chat.models import Message

        return list(
            Message.objects.filter(receiver_id=user_id, read=False)
            .order_by("timestamp")
            .select_related("sender", "receiver")
        )

    async def send_unread_messages(self, user_id):
        unread_messages = await self.get_unread_messages(user_id)
        for message in unread_messages:
            local_timestamp = timezone.localtime(message.timestamp)
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "chat_message",
                        "sender": str(message.sender.id),
                        "receiver": str(message.receiver.id),
                        "message": message.message,
                        "time": local_timestamp.strftime("%H:%M:%S"),
                    }
                )
            )

    @database_sync_to_async
    def mark_message_as_read(self, user_id):
        from chat.models import Message

        messages = Message.objects.filter(
            receiver_id=self.user.id, sender_id=user_id, read=False
        )
        for message in messages:
            message.read = True
            message.save()

    async def chat_message(self, event):
        message = event["message"]
        local_timestamp = timezone.localtime(timezone.now())
        if str(self.user.id) == event["receiver"]:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "chat_message",
                        "message": message,
                        "sender": event["sender"],
                        "receiver": event["receiver"],
                        "time": local_timestamp.strftime("%H:%M:%S"),
                    }
                )
            )

    async def send_status_updates(self):
        for user_id in self.followed_users:
            status = await self.get_user_status(user_id)
            await self.send(
                text_data=json.dumps(
                    {"type": "status_update", "user_id": user_id, "status": status}
                )
            )

    async def subscribe_to_status_updates(self, user_ids):
        for user_id in user_ids:
            await self.channel_layer.group_add(
                f"user_status_{user_id}", self.channel_name
            )
            if user_id not in self.followed_users:
                self.followed_users.append(user_id)

            status = await self.get_user_status(user_id)

            await self.send(
                text_data=json.dumps(
                    {"type": "status_update", "user_id": user_id, "status": status}
                )
            )

    @database_sync_to_async
    def get_user_status(self, user_id):
        r = redis.Redis(host="redis", port=6379, db=0)
        status = r.get(f"user_status:{user_id}")
        if status is not None:
            return status.decode("utf-8")
        return "offline"

    async def can_send_message(self, receiver_id):
        sender = self.user
        receiver = await self.get_user_by_id(receiver_id)
        return not await self.is_user_blocked_by_receiver(sender, receiver)

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_blocked_by_receiver(self, sender, receiver):
        if receiver:
            return receiver.blocked_users.filter(id=sender.id).exists()
        return False

    async def store_message(self, receiver_id, message):
        receiver = await self.get_user_by_id(receiver_id)
        if receiver:
            await self.create_message(self.user, receiver, message)

    @database_sync_to_async
    def is_user_online(self, user_id):
        r = redis.Redis(host="redis", port=6379, db=0)
        return r.exists(f"user_status:{user_id}")

    @database_sync_to_async
    def create_message(self, sender, receiver, message):
        from chat.models import Message

        Message.objects.create(sender=sender, receiver=receiver, message=message)

    async def mark_user_online(self, user_id):
        r = redis.Redis(host="redis", port=6379, db=0)
        r.set(f"user_status:{user_id}", "online")

        await self.channel_layer.group_send(
            f"user_status_{user_id}",
            {
                "type": "status_update",
                "user_id": user_id,
                "status": "online",
            },
        )

    async def mark_user_offline(self, user_id):
        r = redis.Redis(host="redis", port=6379, db=0)
        r.delete(f"user_status:{user_id}")

        await self.channel_layer.group_send(
            f"user_status_{user_id}",
            {
                "type": "status_update",
                "user_id": user_id,
                "status": "offline",
            },
        )

    async def status_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def ping_client(self):
        while self.active:
            await asyncio.sleep(30)
            if not self.pong_received:
                try:
                    await self.close()
                    break
                except RuntimeError:
                    if await self.is_user_online(str(self.user.id)):
                        await self.mark_user_offline(str(self.user.id))
                    break
            else:
                self.pong_received = False
                try:
                    if self.active:
                        await self.send(text_data=json.dumps({"type": "ping"}))
                except RuntimeError:
                    if await self.is_user_online(str(self.user.id)):
                        await self.mark_user_offline(str(self.user.id))
                    break

    async def tournament_message(self, event):
        message = event["message"]
        action = event.get("action")
        tournament_id = event["tournamentId"]
        await self.send(
            text_data=json.dumps(
                {
                    "type": "tournament_message",
                    "message": message,
                    "tournamentId": tournament_id,
                    "action": action,
                }
            )
        )

    async def send_tournament(self, event):
        tournament_id = event["tournamentId"]
        action = event["action"]
        if (action == "join_tournament"):
            await self.channel_layer.group_add(
                f"tournament_{tournament_id}", self.channel_name
            )
            return
        await self.send(
            text_data=json.dumps(
                {
                    "type": "tournament_message",
                    "action": action,
                    "tournamentId": tournament_id,
                    "message": "Tournament " + tournament_id + " is ready",
                }
            )
        )

    async def send_tournament_ready(self, active_tournaments):
        for tournament in active_tournaments:
            await self.channel_layer.group_add(
                f"tournament_{str(tournament.uid)}", self.channel_name
            )
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "tournament_message",
                        "action": "tournament_ready",
                        "tournamentId": str(tournament.uid),
                        "message": "Tournament " + str(tournament.uid) + " is ready",
                    }
                )
            )

    async def send_match(self, event):
        match_id = event["matchId"]
        message = event["message"]
        action = event["action"]
        tournamentId = event.get("tournamentId")

        if (action == "join_match"):
            print(f"Received match event: {event}")
            await self.channel_layer.group_add(f"match_{match_id}", self.channel_name)
            return
        await self.send(
            text_data=json.dumps(
                {
                    "type": "match_message",
                    "action": action,
                    "matchId": match_id,
                    "message": message,
                    "tournamentId": tournamentId,
                }
            )
        )

    async def verify_active_match(self):
        active_matches = await self.get_active_matches()
        await self.send_match_ready(active_matches)

    @database_sync_to_async
    def get_active_matches(self):
        from tournament.models import Matches
        from django.db.models import Q

        active_matches = Matches.objects.filter(
            Q(user1=self.user) | Q(user2=self.user),
            is_active=True,
            is_finished=False,
        )
        return list(active_matches)

    @database_sync_to_async
    def get_tourmanent_uid(self, match):
        return str(match.tournament.uid)

    async def send_match_ready(self, active_matches):
        for match in active_matches:
            tournamentUID = await self.get_tourmanent_uid(match)
            await self.channel_layer.group_add(
                f"match_{str(match.uid)}", self.channel_name
            )
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "match_message",
                        "action": "match_ready",
                        "matchId": str(match.uid),
                        "message": "Match " + str(match.uid) + " is ready for tournament " + tournamentUID,
                        "tournamentId": tournamentUID,
                    }
                )
            )

    async def verify_active_tournament(self):
        active_tournaments = await self.get_active_tournaments()
        await self.send_tournament_ready(active_tournaments)

    @database_sync_to_async
    def get_active_tournaments(self):
        from tournament.models import Tournament

        active_tournaments = Tournament.objects.filter(
            is_active=True, user=self.user, is_finished=False
        )
        return list(active_tournaments)
