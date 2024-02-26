from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
import redis
from django.utils import timezone

# from CustomUser.models import CustomUser


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            # Utiliser l'ID de l'utilisateur pour nommer le groupe
            self.room_group_name = f"chat_{str(self.user.id)}"

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.mark_user_online(str(self.user.id))
            await self.accept()
            await self.send_unread_messages(str(self.user.id))

        else:
            await self.close()


    async def disconnect(self, close_code):
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
    @database_sync_to_async
    def get_unread_messages(self, user_id):
        from chat.models import Message
        return list(Message.objects.filter(receiver_id=user_id, read=False).order_by('timestamp').select_related('sender', 'receiver'))



    async def send_unread_messages(self, user_id):
            unread_messages = await self.get_unread_messages(user_id)
            for message in unread_messages:
                local_timestamp = timezone.localtime(message.timestamp)
                await self.send(text_data=json.dumps({
                    "type": "chat_message",
                    "sender": str(message.sender.id),
                    "receiver": str(message.receiver.id),
                    "message": message.message,
                    "time": local_timestamp.strftime("%H:%M:%S"),
                }))
            await self.mark_message_as_read(user_id)

    @database_sync_to_async
    def mark_message_as_read(self, user_id):
        from chat.models import Message
        messages = Message.objects.filter(receiver_id=user_id, read=False)
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

    async def subscribe_to_status_updates(self, user_ids):
        for user_id in user_ids:
            await self.channel_layer.group_add(
                f"user_status_{user_id}", self.channel_name
            )

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

