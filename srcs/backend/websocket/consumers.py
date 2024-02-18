from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid
import aioredis
from channels.layers import get_channel_layer


class MatchmakingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        if self.scope["user"].is_anonymous:
            await self.send(
                text_data=json.dumps({"message": "You are not authenticated"})
            )
            await self.close()
            return

        self.user_id = str(self.scope["user"].id)

        # Connexion à Redis
        self.redis = await aioredis.from_url(
            "redis://redis:6379", db=0
        )

        # Vérifie si le joueur est déjà en file d'attente
        in_queue = await self.redis.get(f"user_{self.user_id}_ws_channel")
        
        if in_queue:
            await self.send(text_data=json.dumps({"message": "You are already in queue"}))
            await self.close()
            return

        # Stocke le channel name avec l'ID utilisateur dans Redis pour pouvoir envoyer des messages plus tard
        await self.redis.set(f"user_{self.user_id}_ws_channel", self.channel_name)

        # Ajoute un utilisateur à la liste d'attente dans Redis
        await self.redis.lpush("matchmaking_queue", self.user_id)

        # Vérifie si un match peut être fait
        await self.check_for_match()

    async def check_for_match(self):
        queue_length = await self.redis.llen("matchmaking_queue")

        if queue_length >= 2:
            player1_id, player2_id = await self.get_players_from_queue()

            room_id = str(uuid.uuid4())
            room_url = f"/pong/{room_id}/"

            print(f"Match found between {player1_id} and {player2_id} in room {room_url}")

            # Envoyer l'URL de la salle aux deux joueurs
            await self.notify_players_about_match([player1_id, player2_id], room_url)
            await self.redis.delete(f"user_{self.user_id}_ws_channel")
        else:
            await self.send(text_data=json.dumps({"message": "You are in queue"}))

    async def get_players_from_queue(self):
        # Récupère les deux premiers utilisateurs de la liste d'attente et les décode si nécessaire
        player1_id = await self.redis.rpop("matchmaking_queue")
        player2_id = await self.redis.rpop("matchmaking_queue")

        player1_id = player1_id.decode("utf-8") if player1_id else None
        player2_id = player2_id.decode("utf-8") if player2_id else None

        return player1_id, player2_id

    async def notify_players_about_match(self, player_ids, room_url):
        # Récupère les channel names des joueurs et envoie le message
        channel_layer = get_channel_layer()
        for player_id in player_ids:
            player_channel = await self.redis.get(f"user_{player_id}_ws_channel")
            if player_channel:
                await channel_layer.send(
                    player_channel.decode("utf-8"),
                    {
                        "type": "send_message",
                        "text": json.dumps(
                            {
                                "message": "Match found",
                                "room_url": room_url,
                            }
                        ),
                    },
                )

    async def disconnect(self, close_code):
        await self.redis.close()

    async def send_message(self, event):
        await self.send(text_data=event["text"])
