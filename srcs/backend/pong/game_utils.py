# utils.py
import aioredis

def calculate_sleep_duration(delta_time, tick_rate):
    """Calculate sleep duration to maintain a consistent FPS."""
    frame_duration = 1.0 / tick_rate
    return max(0, frame_duration - delta_time)

async def connect_to_redis():
    """Establish a connection to Redis and return the connection object."""
    try:
        return await aioredis.from_url("redis://redis:6379", db=0, encoding="utf-8", decode_responses=True)
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        return None

async def clear_redis_room_data(room_name):
    """Clear all Redis data associated with the game room."""
    redis = await aioredis.from_url("redis://redis:6379", db=0, encoding="utf-8", decode_responses=True)
    room_key_pattern = f"game:{room_name}:*"
    async for key in redis.scan_iter(match=room_key_pattern):
        await redis.delete(key)
    print(f"All Redis room data for {room_name} cleared successfully.")