import asyncio
import json
import aioredis
from .game_config import *

async def game_logic_task(room_name):
    print("olo")
    redis = await aioredis.from_url("redis://redis:6379", db=0, encoding="utf-8", decode_responses=True)
    while True:
        # Your game logic here
        # Example: Update the ball's position
        # Save the updated game state to Redis
        await redis.hset(f"game_state:{room_name}", mapping={"ball": json.dumps("texte")})
        # print("yolo")
        await asyncio.sleep(1/60)  # Run the loop at 60 FPS or adjust as needed

