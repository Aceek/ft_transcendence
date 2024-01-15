import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Received message: {text_data}")

        # Handle the received message here

        # Example: echo the message back to the client
        await self.send(text_data=json.dumps({
            'type': 'chat.message',
            'content': data['content'],
        }))
