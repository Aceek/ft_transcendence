from ..game.config import SCREEN_HEIGHT, PADDLE_HEIGHT, PADDLE_SPEED
from ..game.enum import PlayerPosition

class Paddle:
    def __init__(self, user_id, redis_ops):
        self.user_id = user_id
        self.redis_ops = redis_ops
        self.side = None  # Will be an instance of PlayerPosition or None
        # Initialize the position key map
        self.position_key_map = {
            PlayerPosition.LEFT: "lp_y",
            PlayerPosition.RIGHT: "rp_y"
        }

    async def assignment(self):
        for position in [PlayerPosition.LEFT, PlayerPosition.RIGHT]:
            key = f"game:{self.redis_ops.room_name}:paddle:{self.position_key_map[position]}"
            if await self.redis_ops.connection.sismember(key, self.user_id):
                self.side = position
                break
        else:
            for position in [PlayerPosition.LEFT, PlayerPosition.RIGHT]:
                key = f"game:{self.redis_ops.room_name}:paddle:{self.position_key_map[position]}"
                if not await self.redis_ops.connection.scard(key):
                    await self.redis_ops.connection.sadd(key, self.user_id)
                    self.side = position
                    break
        print(f"User {self.user_id} assigned to {self.side.name} paddle")

    async def check_movement(self, new_y):
        # First, check if the requested Y is outside the game boundaries
        if new_y < 0 or new_y > SCREEN_HEIGHT - PADDLE_HEIGHT:
            print(f"Requested Y: {new_y} is outside the game boundaries.")
            return False  # Return False directly if requested Y is outside boundaries

        # If within boundaries, proceed with checking against current position and speed limit
        key = self.position_key_map[self.side]
        current_y_str = await self.redis_ops.get_dynamic_value(key)
        current_y = int(current_y_str) if current_y_str is not None else 0

        # Calculate the attempted movement distance
        movement_distance = abs(new_y - current_y)

        # Check if the movement is within the allowed speed limit
        if movement_distance <= PADDLE_SPEED:
            # await self.set_to_data_redis(new_y)  # If the movement is valid, update the paddle position in Redis
            return True
        else:
            print(f"Attempted to move the paddle more than the speed limit ({PADDLE_SPEED}). Movement Distance: {movement_distance}")  # Print error message
            return False

    async def set_data_to_redis(self, paddle_y):
        key = self.position_key_map[self.side]
        await self.redis_ops.set_dynamic_value(key, paddle_y)
