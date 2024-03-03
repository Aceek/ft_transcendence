from ..game.config import *
from ..game.enum import PlayerPosition
from ..game.utils import get_player_key_map


class Paddle:
    def __init__(self, user_id, redis_ops):
        self.user_id = user_id
        self.redis_ops = redis_ops
        self.side = None

        self.size = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED

        self.boundary_min = 0
        self.collision_boundary_min = PADDLE_BORDER_DISTANCE
        self.other_collision_boundary_min = PADDLE_BORDER_DISTANCE
        
        self.boundary_max = None
        self.collision_boundary_max = None
        self.other_collision_boundary_max = None
        
        self.min_relevant_position = None
        self.max_relevant_position = None

        self.axis_key = None
        self.reverse_axis_key = None

    async def get_collision_details(self, boundary_condition):
        # Define a mapping of which paddle positions to check based on the current paddle's position
        # and whether it's at its min or max boundary.
        collision_map = {
            PlayerPosition.LEFT: {
                "min": (PlayerPosition.UP, "min"),
                "max": (PlayerPosition.BOTTOM, "min")
            },
            PlayerPosition.RIGHT: {
                "min": (PlayerPosition.UP, "max"),
                "max": (PlayerPosition.BOTTOM, "max")
            },
            PlayerPosition.UP: {
                "min": (PlayerPosition.LEFT, "min"),
                "max": (PlayerPosition.RIGHT, "min")
            },
            PlayerPosition.BOTTOM: {
                "min": (PlayerPosition.LEFT, "max"),
                "max": (PlayerPosition.RIGHT, "max")
            }
        }
        if self.side in collision_map:
            return collision_map[self.side][boundary_condition]
        

    async def set_boundaries(self):
        if self.side in [PlayerPosition.BOTTOM, PlayerPosition.UP]:
            self.boundary_max = SCREEN_WIDTH
            self.collision_boundary_max = SCREEN_WIDTH - PADDLE_BORDER_DISTANCE
            self.other_collision_boundary_max = SCREEN_HEIGHT - PADDLE_BORDER_DISTANCE
        else:
            self.boundary_max = SCREEN_HEIGHT
            self.collision_boundary_max = SCREEN_HEIGHT - PADDLE_BORDER_DISTANCE
            self.other_collision_boundary_max = SCREEN_WIDTH - PADDLE_BORDER_DISTANCE

    async def set_axis_keys(self):
        self.axis_key = 'paddle_x' if self.side in [PlayerPosition.BOTTOM, PlayerPosition.UP] else 'paddle_y'
        self.reverse_axis_key = 'paddle_y' if self.axis_key == 'paddle_x' else 'paddle_x'

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

    async def check_movement(self, new_pos):
        # Determine the axis and boundary based on the player's side
        current_pos_str = await self.redis_ops.get_dynamic_value(self.key_map[self.axis_key])
        current_pos = int(current_pos_str) if current_pos_str is not None else 0

        # Check game boundaries
        if new_pos < self.boundary_min or new_pos + self.size > self.boundary_max:
            print(f"Requested position: {new_pos} is outside the game boundaries.")
            return False

        # Check movement speed limit
        movement_distance = abs(new_pos - current_pos)
        if movement_distance > self.speed:
            print(f"Attempted to move the paddle more than the speed limit ({self.speed}). Movement Distance: {movement_distance}")
            return False

        # Early exit if only 2 players
        if PLAYER_NB < 3:
            return True

        # Check if the paddle is in potential range of others
        relevant_position = None
        if new_pos <= self.collision_boundary_min:
            relevant_position, relevant_boundary = await self.get_collision_details("min")
        elif new_pos + self.size >= self.collision_boundary_max:
            relevant_position, relevant_boundary = await self.get_collision_details("max")

        # Check if there is a collision
        if relevant_position is not None:
            other_key_map = get_player_key_map(relevant_position)
            other_paddle_pos_str = await self.redis_ops.get_dynamic_value(other_key_map[self.reverse_axis_key])
            
            # Other player does not exist in the game, thus no need to check
            if other_paddle_pos_str is None:
                return True
            else:
                other_paddle_pos = int(other_paddle_pos_str)
            
            if relevant_boundary == "min" and other_paddle_pos <= self.other_collision_boundary_min or \
            relevant_boundary == "max" and other_paddle_pos + self.size >= self.other_collision_boundary_max:
                print(f"Overlap detected with {relevant_position} paddle.")
                return False

        return True

    async def set_data_to_redis(self, new_position):
        # Choose the correct axis key based on the player's side
        key = self.key_map['paddle_x'] if self.side in [PlayerPosition.BOTTOM, PlayerPosition.UP] else self.key_map['paddle_y']
        await self.redis_ops.set_dynamic_value(key, new_position)
