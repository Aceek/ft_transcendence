from .config import *
from .enum import PlayerPosition

class Player:
    def __init__(self, side, redis_ops):
        self.side = side
        self.reset_value()
        self.redis_ops = redis_ops

    def reset_value(self):
        self.score = INITIAL_SCORE
        self.paddle_y = INITIAL_PADDLE_Y
        self.score_updated = False

    async def set_to_redis(self):
        await self.set_paddle_to_redis(self.paddle_y)
        await self.set_score_to_redis(self.score)

    def update_score(self):
        self.score += 1
        self.score_updated = True

    def reset_score_update_flag(self):
        self.score_updated = False

#------------------------------REDIS-------------------------------------

    async def set_score_to_redis(self, score):
        key = "lp_s" if self.side == PlayerPosition.LEFT else "rp_s"
        await self.redis_ops.set_dynamic_value(key, score)
        # Print statement after setting score to Redis
        # print(f"Set score {score} for player {self.side} in Redis with key {key}")

    async def set_paddle_to_redis(self, paddle_y):
        key = "lp_y" if self.side == PlayerPosition.LEFT else "rp_y"  # Assuming this was a typo in your original code and should be lp_y/rp_y for paddle position
        await self.redis_ops.set_dynamic_value(key, paddle_y)
        # Print statement after setting paddle position to Redis
        # print(f"Set paddle position {paddle_y} for player {self.side} in Redis with key {key}")

    async def get_paddle_from_redis(self):
        """
        Get the Y positions of the paddles from Redis and update the players' positions.
        """
        key = "lp_y" if self.side == PlayerPosition.LEFT else "rp_y"  # Adjusted to match the set_paddle_to_redis correction
        paddle_position_str = await self.redis_ops.get_dynamic_value(key)
        self.paddle_y = int(paddle_position_str)
        # Print statement after getting paddle position from Redis
        # print(f"Got paddle position {self.paddle_y} for player {self.side} from Redis with key {key}")
