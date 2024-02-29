import aioredis

from ..game.enum import GameStatus

class RedisOps:
    def __init__(self, room_name):
        self.redis_url = "redis://redis:6379"
        self.room_name = room_name
        self.connection = None

    @classmethod
    async def create(cls, room_name):
        instance = cls(room_name)
        instance.connection = await instance.connect()
        if instance.connection is None:
            raise Exception("Failed to create Redis connection.")
        return instance

    async def connect(self):
        """Establish a connection to Redis and return the connection object."""
        try:
            return aioredis.from_url(self.redis_url, db=0, encoding="utf-8", decode_responses=True)
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            return None

    async def clear_all_data(self):
        """Clear all Redis data associated with the game room."""
        room_key_pattern = f"game:{self.room_name}:*"
        async for key in self.connection.scan_iter(match=room_key_pattern):
            await self.connection.delete(key)
        print(f"All Redis room data for {self.room_name} cleared successfully.")

# -------------------------------SET-----------------------------------
        
    async def set_static_data(self, data):
        key = f"game:{self.room_name}:static"
        await self.connection.hset(key, mapping=data)

    async def set_dynamic_value(self, field_name, value):
        """Set a specific value from the dynamic data of a game room."""
        key = f"game:{self.room_name}:dynamic"
        await self.connection.hset(key, field_name, value)

    async def set_dynamic_data(self, data):
        key = f"game:{self.room_name}:dynamic"
        await self.connection.hset(key, mapping=data)

    async def set_game_status(self, new_status: GameStatus):
        await self.set_dynamic_value("gs", int(new_status.value))

# -------------------------------GET-----------------------------------

    async def get_static_data(self):
        key = f"game:{self.room_name}:static"
        return await self.connection.hgetall(key)
    
    async def get_dynamic_value(self, field_name):
        """Retrieve a specific value from the dynamic data of a game room."""
        key = f"game:{self.room_name}:dynamic"
        value = await self.connection.hget(key, field_name)
        return value
    
    async def get_dynamic_data(self):
        key = f"game:{self.room_name}:dynamic"
        return await self.connection.hgetall(key)

    async def get_game_status(self):
        current_status = await self.get_dynamic_value("gs")
        if current_status:
            return GameStatus(int(current_status))
        return None

    async def get_connected_users(self):
        key = f"game:{self.room_name}:connected_users"
        return await self.connection.scard(key)
    
    async def get_restart_requests(self):
        key = f"game:{self.room_name}:restart_requests"
        return await self.connection.scard(key)

# -------------------------------ADD-----------------------------------

    async def add_game_logic_flag(self):
        """Set the game logic flag, indicating that the game logic can proceed."""
        flag_key = f"game:{self.room_name}:logic_flag"
        flag_set = await self.connection.setnx(flag_key, "true")
        if flag_set:
            print(f"Logic flag set for room: {self.room_name}")
        return flag_set

    async def add_connected_users(self, user_id):
        key = f"game:{self.room_name}:connected_users"
        await self.connection.sadd(key, user_id)
        print(f"Add user {user_id} from connected users in room: {self.room_name}")
    
    async def add_restart_requests(self, user_id):
        key = f"game:{self.room_name}:restart_requests"
        await self.connection.sadd(key, user_id)
        print(f"Add user {user_id} to restart requests in room: {self.room_name}")

# -------------------------------DEL-----------------------------------
    
    async def del_game_logic_flag(self):
        flag_key = f"game:{self.room_name}:logic_flag"
        await self.connection.delete(flag_key)
        print(f"Logic flag deleted for room: {self.room_name}")

    async def del_connected_user(self, user_id):
        key = f"game:{self.room_name}:connected_users"
        await self.connection.srem(key, user_id)
        print(f"Removed user {user_id} from connected users in room: {self.room_name}")
        
    async def del_restart_request(self, user_id):
        key = f"game:{self.room_name}:restart_requests"
        await self.connection.srem(key, user_id)
        print(f"Removed user {user_id} to restart requests in room: {self.room_name}")
    
    async def del_all_restart_requests(self):
        key = f"game:{self.room_name}:restart_requests"
        await self.connection.delete(key)
        print(f"Cleared all restart requests for room: {self.room_name}")





    # Add more Redis operations as needed...

    # async def close(self):
    #     self.connection.close()
    #     await self.connection.wait_closed()