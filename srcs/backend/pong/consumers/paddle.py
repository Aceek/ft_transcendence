from ..game.enum import PlayerPosition
from ..game.utils import get_player_key_map
from ..game.config import PADDLE_HEIGHT, PADDLE_SPEED, PADDLE_BORDER_DISTANCE,\
                          SCREEN_HEIGHT, SCREEN_WIDTH

class Paddle:
    def __init__(self, user_id, redis_ops, player_nb):
        self.user_id = user_id
        self.redis_ops = redis_ops
        self.player_nb = player_nb
        self.position = None

        self.size = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED
        self.border_distance = PADDLE_BORDER_DISTANCE

        self.screen_height = SCREEN_HEIGHT
        self.screen_width = SCREEN_WIDTH
        if self.player_nb > 2:
            self.screen_width = self.screen_height

        self.boundary_min = 0
        self.collision_boundary_min = self.border_distance
        self.other_collision_boundary_min = self.border_distance
        
        self.boundary_max = None
        self.collision_boundary_max = None
        self.other_collision_boundary_max = None
        
        self.min_relevant_position = None
        self.max_relevant_position = None

        self.axis_key = None
        self.reverse_axis_key = None
        
        self.last_pos = None

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
        if self.position in collision_map:
            return collision_map[self.position][boundary_condition]

    async def set_boundaries(self):
        if self.position in [PlayerPosition.BOTTOM, PlayerPosition.UP]:
            self.boundary_max = self.screen_width
            self.collision_boundary_max = self.screen_width - self.border_distance
            self.other_collision_boundary_max = self.screen_height - self.border_distance
        else:
            self.boundary_max = self.screen_height
            self.collision_boundary_max = self.screen_height - self.border_distance
            self.other_collision_boundary_max = self.screen_width - self.border_distance

    async def set_axis_keys(self):
        self.axis_key = 'paddle_x' if self.position in [PlayerPosition.BOTTOM, PlayerPosition.UP] else 'paddle_y'
        self.reverse_axis_key = 'paddle_y' if self.axis_key == 'paddle_x' else 'paddle_x'

    async def assignment(self, game_mode, player_nb, positions):
        # Attempt to acquire a lock for the paddle assignment process
        lock_key = f"game:{self.redis_ops.room_name}:lock:assignment"
        lock = self.redis_ops.connection.lock(lock_key, timeout=5)
        await lock.acquire()

        try:
            # Check if the user is already assigned a position
            for position in PlayerPosition:
                # Skip already assigned positions for offline mode. This has no effect for online mode.
                if game_mode == "offline" and position in positions:
                    continue

                self.key_map = get_player_key_map(position)
                key = f"game:{self.redis_ops.room_name}:paddle:{self.key_map['position']}"

                if await self.redis_ops.connection.sismember(key, self.user_id):
                    self.position = position
                    return True, position

            # If not already assigned, attempt to assign a new position based on order
            assigned_positions = 0
            for position in PlayerPosition:
                if assigned_positions >= player_nb:
                    break  # Stop if the maximum number of players is reached

                self.key_map = get_player_key_map(position)
                key = f"game:{self.redis_ops.room_name}:paddle:{self.key_map['position']}"
                assigned_count = await self.redis_ops.connection.scard(key)

                if assigned_count == 0:  # Position is available
                    await self.redis_ops.connection.sadd(key, self.user_id)
                    self.position = position
                    return True, position

                assigned_positions += assigned_count

            # If all positions are filled or the player is beyond the maximum count, assign as spectator
            print(f"All positions filled or player_nb exceeded, user {self.user_id} is a spectator.")
            self.position = PlayerPosition.SPEC
            return False, PlayerPosition.SPEC
        finally:
            await lock.release()

    # async def check_movement(self, new_pos):
    #     # Determine the axis and boundary based on the player's position
    #     current_pos_str = await self.redis_ops.get_dynamic_value(self.key_map[self.axis_key])
    #     current_pos = int(current_pos_str)

    #     # Check game boundaries
    #     if new_pos < self.boundary_min or new_pos + self.size > self.boundary_max:
    #         return False

    #     # Check movement speed limit
    #     if new_pos < current_pos - self.speed or new_pos > current_pos + self.speed:
    #         print(f"Abnormal paddle position based on paddle speed ans server tick rate ({self.speed})")
    #         return False

    #     # Early exit if only 2 players
    #     if self.player_nb < 3:
    #         return True

    #     # Check if the paddle is in potential range of others
    #     relevant_position = None
    #     if new_pos <= self.collision_boundary_min:
    #         relevant_position, relevant_boundary = await self.get_collision_details("min")
    #     elif new_pos + self.size >= self.collision_boundary_max:
    #         relevant_position, relevant_boundary = await self.get_collision_details("max")

    #     # If a potentially colliding position is found
    #     if relevant_position is not None:
    #         other_key_map = get_player_key_map(relevant_position)
    #         other_paddle_pos_str = await self.redis_ops.get_dynamic_value(other_key_map[self.reverse_axis_key])
            
    #         # Other player does not exist in the game, thus no need to check
    #         if other_paddle_pos_str is None:
    #             return True
    #         else:
    #             other_paddle_pos = int(other_paddle_pos_str)

    #         # Checking collision based on boundaries
    #         if relevant_boundary == "min" and other_paddle_pos <= self.other_collision_boundary_min:
    #             return False
    #         elif relevant_boundary == "max" and other_paddle_pos + self.size >= self.other_collision_boundary_max:
    #             return False

    #     self.last_pos = new_pos
    #     return True

    async def set_data_to_redis(self, new_position):
        # Choose the correct axis key based on the player's side
        key = self.key_map['paddle_x'] if self.position in [PlayerPosition.BOTTOM, PlayerPosition.UP] else self.key_map['paddle_y']
        await self.redis_ops.set_dynamic_value(key, new_position)
