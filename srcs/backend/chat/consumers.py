from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
import redis


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            # Utiliser l'ID de l'utilisateur pour nommer le groupe
            self.room_group_name = f"chat_{str(self.user.id)}"

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.mark_user_online(str(self.user.id))
            await self.accept()
        else:
            await self.close()

        # Envoi d'un message de bienvenue by random uid
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": "Hello, World!",
                "sender": "cd47dba1-ad19-4fb2-9c32-9311f0beae7d",
                "receiver": str(self.user.id),
            },
        )
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": "Salut je suis newuser",
                "sender": "cd47dba1-ad19-4fb2-9c32-9311f0beae7d",
                "receiver": str(self.user.id),
            },
        )

    async def disconnect(self, close_code):
        await self.mark_user_offline(str(self.user.id))
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        receiver_id = data["receiver"]
        receiver_group_name = f"chat_{receiver_id}"
        print("message", message)

        if await self.can_send_message(receiver_id):
            if not await self.is_user_online(receiver_id):
                await self.store_message(receiver_id, message)
            else:
                await self.channel_layer.group_send(
                    receiver_group_name,
                    {
                        "type": "chat_message",
                        "message": message,
                        "sender": str(self.user.id),
                        "receiver": receiver_id,
                    },
                )

    async def chat_message(self, event):
        message = event["message"]
        if str(self.user.id) == event["receiver"]:
            await self.send(
                text_data=json.dumps(
                    {
                        "message": message,
                        "sender": event["sender"],
                        "receiver": event["receiver"],
                        "time": "13:59:59",
                    }
                )
            )

    async def can_send_message(self, receiver_id):
        receiver = await self.get_user_by_id(receiver_id)
        return not await self.is_user_blocked(receiver)

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_blocked(self, receiver):
        if receiver:
            return self.user.blocked_users.filter(id=receiver.id).exists()
        return False

    async def store_message(self, receiver_id, message):
        receiver = await self.get_user_by_id(receiver_id)
        if receiver:
            await self.create_message(self.user, receiver, message)

    @database_sync_to_async
    def mark_user_offline(self, user_username):
        r = redis.Redis(host="redis", port=6379, db=0)
        r.delete(f"user_status:{user_username}")

    @database_sync_to_async
    def is_user_online(self, user_id):
        r = redis.Redis(host="redis", port=6379, db=0)
        return r.exists(f"user_status:{user_id}")

    @database_sync_to_async
    def create_message(self, sender, receiver, message):
        from chat.models import Message

        Message.objects.create(sender=sender, receiver=receiver, message=message)

    @database_sync_to_async
    def mark_user_online(self, user_id):
        r = redis.Redis(host="redis", port=6379, db=0)
        r.set(f"user_status:{user_id}", "online")
