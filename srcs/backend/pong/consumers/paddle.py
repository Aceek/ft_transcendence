from ..game.config import *
from ..game.enum import PlayerPosition
from ..game.utils import get_player_key_map


class Paddle:
    def __init__(self, user_id, redis_ops):
        self.user_id = user_id
        self.redis_ops = redis_ops
        self.side = None

    async def assignment(self):
        # Iterate through all possible positions
        for position in PlayerPosition:
            # Use get_player_key_map to fetch the key map for the current position
            self.key_map = get_player_key_map(position)

            # Construct the Redis key using the position from the key map
            key = f"game:{self.redis_ops.room_name}:paddle:{self.key_map['position']}"
            
            # Check if the user_id is already assigned to a paddle for this position
            if await self.redis_ops.connection.sismember(key, self.user_id):
                self.side = position
                return
            # Check if there's room to add a new player to this position
            elif not await self.redis_ops.connection.scard(key):
                await self.redis_ops.connection.sadd(key, self.user_id)
                self.side = position
                return

        # This prints the side to which the user was assigned, if any
        if self.side is not None:
            print(f"User {self.user_id} assigned to {self.side.name} paddle")
        else:
            print(f"No available position for user {self.user_id}.")

    async def check_movement(self, new_position):
        # Choose the correct axis key based on the player's side
        key = self.key_map['paddle_x'] if self.side in [PlayerPosition.BOTTOM, PlayerPosition.UP] else self.key_map['paddle_y']
        current_pos_str = await self.redis_ops.get_dynamic_value(key)
        current_pos = int(current_pos_str) if current_pos_str is not None else 0

        # Calculate the attempted movement distance
        movement_distance = abs(new_position - current_pos)
        # Determine boundaries based on paddle orientation
        boundary = SCREEN_WIDTH - PADDLE_WIDTH if self.side in [PlayerPosition.BOTTOM, PlayerPosition.UP] else SCREEN_HEIGHT - PADDLE_HEIGHT

        if new_position < 0 or new_position > boundary:
            print(f"Requested position: {new_position} is outside the game boundaries.")
            return False

        # Check if the movement is within the allowed speed limit
        if movement_distance <= PADDLE_SPEED:
            return True
        else:
            print(f"Attempted to move the paddle more than the speed limit ({PADDLE_SPEED}). Movement Distance: {movement_distance}")
            return False

    async def set_data_to_redis(self, new_position):
        # Choose the correct axis key based on the player's side
        key = self.key_map['paddle_x'] if self.side in [PlayerPosition.BOTTOM, PlayerPosition.UP] else self.key_map['paddle_y']
        await self.redis_ops.set_dynamic_value(key, new_position)
