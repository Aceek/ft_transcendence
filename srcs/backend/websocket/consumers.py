from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

class MatchmakingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        print("user", self.scope["user"])
        # await self.check_for_match()

    async def disconnect(self, close_code):
        await self.remove_user_from_queue()

    async def check_for_match(self):
        queue_count = await self.get_queue_count()
        if queue_count >= 2:
            queue_entries = await self.get_first_two_queue_entries()
            room = await self.create_room()
            room_url = f"/room/{room.id}/"
            
            for queue_entry in queue_entries:
                await self.channel_layer.send(
                    queue_entry.websocket_id,
                    {
                        "type": "match_found",
                        "room_url": room_url,
                    },
                )
            await self.remove_queue_entries(queue_entries)
        else:
            await self.send(text_data=json.dumps({"message": "You are in queue"}))

    @database_sync_to_async
    def add_user_to_queue(self, user):
        from .models import MatchmakingQueue
        queue_entry, created = MatchmakingQueue.objects.get_or_create(user=user)
        queue_entry.websocket_id = self.channel_name
        queue_entry.save()
    
    @database_sync_to_async
    def remove_user_from_queue(self):
        from .models import MatchmakingQueue
        MatchmakingQueue.objects.filter(websocket_id=self.channel_name).delete()

    @database_sync_to_async
    def get_queue_count(self):
        from .models import MatchmakingQueue
        return MatchmakingQueue.objects.count()

    @database_sync_to_async
    def get_first_two_queue_entries(self):
        from .models import MatchmakingQueue
        return list(MatchmakingQueue.objects.all()[:2])

    @database_sync_to_async
    def create_room(self):
        from .models import MatchmakingRoom
        return MatchmakingRoom.objects.create()

    @database_sync_to_async
    def remove_queue_entries(self, queue_entries):
        from .models import MatchmakingQueue
        MatchmakingQueue.objects.filter(id__in=[entry.id for entry in queue_entries]).delete()


