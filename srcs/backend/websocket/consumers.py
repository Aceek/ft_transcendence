from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json


# class MatchmakingConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()

#         user = self.get_user()

#         await self.add_user_to_queue(user)

#         await self.check_for_match()

#     async def disconnect(self, close_code):
#         await self.remove_user_from_queue()

#     async def check_for_match(self):
#         queue_count = await self.get_queue_count()
#         if queue_count >= 2:
#             queue_entries = await self.get_first_two_queue_entries()
#             database_sync_to_async(print(queue_entries))

#             room = await self.create_room(queue_entries[0].user, queue_entries[1].user)
#             room_url = f"/room/{room.id}/"

#             for queue_entry in queue_entries:
#                 await self.channel_layer.send(
#                     queue_entry.websocket_id,
#                     {
#                         "type": "match_found",
#                         "room_url": room_url,
#                     },
#                 )
#             await self.remove_queue_entries(queue_entries)
#         else:
#             await self.send(text_data=json.dumps({"message": "You are in queue"}))

#     @database_sync_to_async
#     def add_user_to_queue(self, user):
#         from .models import MatchmakingQueue
#         queue_entry, created = MatchmakingQueue.objects.get_or_create(user=user)
#         queue_entry.websocket_id = self.channel_name
#         queue_entry.save()

#     @database_sync_to_async
#     def remove_user_from_queue(self):
#         from .models import MatchmakingQueue

#         MatchmakingQueue.objects.filter(websocket_id=self.channel_name).delete()

#     @database_sync_to_async
#     def get_queue_count(self):
#         from .models import MatchmakingQueue

#         return MatchmakingQueue.objects.count()

#     @database_sync_to_async
#     def get_first_two_queue_entries(self):
#         from .models import MatchmakingQueue

#         return print(list(MatchmakingQueue.objects.all()[:2]))

#     @database_sync_to_async
#     def create_room(self, player1, player2):
#         from .models import MatchmakingRoom
#         return MatchmakingRoom.objects.create(player1=player1, player2=player2)


#     @database_sync_to_async
#     def remove_queue_entries(self, queue_entries):
#         from .models import MatchmakingQueue

#         MatchmakingQueue.objects.filter(
#             id__in=[entry.id for entry in queue_entries]
#         ).delete()

#     def get_user(self):
#         return self.scope["user"]

import hashlib
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
            room_url = f"/room/{room_id}/"

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
