from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid


class MatchmakingConsumer(AsyncWebsocketConsumer):
    queue = []

    async def connect(self):
        await self.accept()

        if self.scope["user"].is_anonymous:
            self.send(text_data=json.dumps({"message": "You are not authenticated"}))
            await self.close()
            return

        self.queue.append(self)

        await self.check_for_match()

    async def check_for_match(self):
        if len(self.queue) >= 2:
            player1 = self.queue.pop(0)
            player2 = self.queue.pop(0)

            # create room
            room_id = str(uuid.uuid4())
            room_url = f"/pong/{room_id}/"

            # send room url to players
            await player1.send(
                text_data=json.dumps({"message": "Match found", "room_url": room_url})
            )
            await player2.send(
                text_data=json.dumps({"message": "Match found", "room_url": room_url})
            )

            # close connection
            await player1.close()
            await player2.close()

        else:
            await self.send(text_data=json.dumps({"message": "You are in queue"}))

    async def disconnect(self, close_code):
        if self in self.queue:
            self.queue.remove(self)
