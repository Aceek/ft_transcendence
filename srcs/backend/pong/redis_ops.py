# redis_ops.py
import aioredis

class RedisOps:
    def __init__(self, room_name):
        self.room_name = room_name
        self.redis = None

    @property
    def connection(self):
        return self.redis

    @classmethod
    async def create(cls, room_name):
        instance = cls(room_name)
        instance.redis = await instance.connect()
        if instance.redis is None:
            raise Exception("Failed to create Redis connection.")
        return instance

    async def connect(self):
        """Establish a connection to Redis and return the connection object."""
        try:
            return aioredis.from_url("redis://redis:6379", db=0, encoding="utf-8", decode_responses=True)
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            return None

    async def clear_data(self, room_name):
        """Clear all Redis data associated with the game room."""
        room_key_pattern = f"game:{room_name}:*"
        async for key in self.redis.scan_iter(match=room_key_pattern):
            await self.redis.delete(key)
        print(f"All Redis room data for {room_name} cleared successfully.")

    async def set_static_data(self, room_name, data):
        key = f"game:{room_name}:static"
        await self.redis.hset(key, mapping=data)

    async def get_static_data(self, room_name):
        key = f"game:{room_name}:static"
        return await self.redis.hgetall(key)
    
    async def get_dynamic_value(self, room_name, field_name):
        """Retrieve a specific value from the dynamic data of a game room."""
        key = f"game:{room_name}:dynamic"
        value = await self.redis.hget(key, field_name)
        return value
    
    async def set_dynamic_value(self, room_name, field_name, value):
        """Set a specific value from the dynamic data of a game room."""
        key = f"game:{room_name}:dynamic"
        await self.redis.hset(key, field_name, value)

    async def set_dynamic_data(self, room_name, data):
        key = f"game:{room_name}:dynamic"
        await self.redis.hset(key, mapping=data)

    async def get_dynamic_data(self, room_name):
        key = f"game:{room_name}:dynamic"
        return await self.redis.hgetall(key)

    # Add more Redis operations as needed...

    # async def close(self):
    #     self.redis.close()
    #     await self.redis.wait_closed()