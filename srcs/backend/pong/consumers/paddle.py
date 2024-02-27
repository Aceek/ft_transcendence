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
        if new_y < 0:
            new_y = 0
            print(f"Clamping paddle move to 0.")
        elif new_y > SCREEN_HEIGHT - PADDLE_HEIGHT:
            new_y = SCREEN_HEIGHT - PADDLE_HEIGHT
            print(f"Clamping paddle move to {SCREEN_HEIGHT - PADDLE_HEIGHT}.")

        key = self.position_key_map[self.side]
        current_y = await self.redis_ops.get_dynamic_value(key)
        current_y = int(current_y) if current_y is not None else 0

        if abs(new_y - current_y) <= PADDLE_SPEED:
            return True
        else:
            print(f"Attempted to move the paddle more than the speed limit.")
            return False

    async def set_to_redis(self, paddle_y):
        key = self.position_key_map[self.side]
        await self.redis_ops.set_dynamic_value(key, paddle_y)
        # print(f"Set paddle position {paddle_y} for player {self.side.name} in Redis with key {key}")
