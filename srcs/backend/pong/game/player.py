from .config import *
from .enum import PlayerPosition
from .utils import get_player_key_map

class Player:
    def __init__(self, side, redis_ops):
        self.side = side
        self.reset_value()
        self.redis_ops = redis_ops
        self.key_map = get_player_key_map(side)
        
        self.speed = PADDLE_SPEED
        if self.side == PlayerPosition.LEFT or self.side == PlayerPosition.RIGHT:
            self.paddle_height = PADDLE_HEIGHT
            self.paddle_width = PADDLE_WIDTH
        elif self.side == PlayerPosition.BOTTOM or self.side == PlayerPosition.UP:
            self.paddle_height = PADDLE_WIDTH
            self.paddle_width = PADDLE_HEIGHT

    def reset_value(self):
        self.score = SCORE_START
        if self.side == PlayerPosition.LEFT:
            self.paddle_x = PADDLE_BORDER_DISTANCE
            self.paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        elif self.side == PlayerPosition.RIGHT:
            self.paddle_x = SCREEN_WIDTH - PADDLE_WIDTH - PADDLE_BORDER_DISTANCE
            self.paddle_y =  SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        elif self.side == PlayerPosition.BOTTOM:
            self.paddle_x = SCREEN_WIDTH // 2 - PADDLE_HEIGHT // 2
            self.paddle_y = SCREEN_HEIGHT - PADDLE_WIDTH - PADDLE_BORDER_DISTANCE
        elif self.side == PlayerPosition.UP:
            self.paddle_x = SCREEN_WIDTH // 2 - PADDLE_HEIGHT // 2
            self.paddle_y = PADDLE_BORDER_DISTANCE
        
#------------------------------CONDITION-------------------------------------

    def check_win(self):
        return self.score >= SCORE_LIMIT

#------------------------------REDIS-------------------------------------


    async def set_data_to_redis(self):
        await self.set_paddle_to_redis(self.paddle_x, "paddle_x")
        await self.set_paddle_to_redis(self.paddle_y, "paddle_y")
        await self.set_score_to_redis(self.score)
        
    async def update_score(self):
        self.score += 1
        await self.set_score_to_redis(self.score)

    async def set_score_to_redis(self, score):
        key = self.key_map["score"]
        await self.redis_ops.set_dynamic_value(key, score)

    async def set_paddle_to_redis(self, new_position, paddle_key):
        key = self.key_map[paddle_key]
        await self.redis_ops.set_dynamic_value(key, new_position)

    async def get_paddle_from_redis(self):
        if self.side in [PlayerPosition.LEFT, PlayerPosition.RIGHT]:
            key = self.key_map["paddle_y"]
            paddle_position_str = await self.redis_ops.get_dynamic_value(key)
            self.paddle_y = int(paddle_position_str)
        else:
            key = self.key_map["paddle_x"]
            paddle_position_str = await self.redis_ops.get_dynamic_value(key)
            self.paddle_x = int(paddle_position_str)