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

    async def set_data_to_redis(self):
        await self.set_paddle_to_redis(self.paddle_y)
        await self.set_score_to_redis(self.score)

    async def update_score(self):
        self.score += 1
        await self.set_score_to_redis(self.score)
        
#------------------------------CONDITION-------------------------------------

    def check_win(self):
        return self.score >= SCORE_LIMIT

#------------------------------REDIS-------------------------------------

    async def set_score_to_redis(self, score):
        key = "lp_s" if self.side == PlayerPosition.LEFT else "rp_s"
        await self.redis_ops.set_dynamic_value(key, score)

    async def set_paddle_to_redis(self, paddle_y):
        key = "lp_y" if self.side == PlayerPosition.LEFT else "rp_y" 
        await self.redis_ops.set_dynamic_value(key, paddle_y)

    async def get_paddle_from_redis(self):
        """
        Get the Y positions of the paddles from Redis and update the players' positions.
        """
        key = "lp_y" if self.side == PlayerPosition.LEFT else "rp_y"
        paddle_position_str = await self.redis_ops.get_dynamic_value(key)
        self.paddle_y = int(paddle_position_str)
