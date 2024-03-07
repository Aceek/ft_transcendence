import json
import uuid
from channels.db import database_sync_to_async


class ChallengeUserMixin:
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
        return f"/pong/online/2/standard/{room_id}"

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
