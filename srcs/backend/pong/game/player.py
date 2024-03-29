from .enum import PlayerPosition
from .utils import get_player_key_map

class Player:
    def __init__(self, position, game, user, username):
        self.position = position
        self.id = position.value
        self.game = game
        self.user = user
        self.username = username
        self.redis_ops = game.redis_ops

        if self.position == PlayerPosition.LEFT or self.position == PlayerPosition.RIGHT:
            self.paddle_height = self.game.paddle_height
            self.paddle_width = self.game.paddle_width
        elif self.position == PlayerPosition.BOTTOM or self.position == PlayerPosition.UP:
            self.paddle_height = self.game.paddle_width
            self.paddle_width = self.game.paddle_height
        self.speed = self.game.paddle_speed

        self.key_map = get_player_key_map(position)
        self.reset_value()

    def reset_value(self):
        self.score = self.game.score_start
        if self.position == PlayerPosition.LEFT:
            self.paddle_x = self.game.paddle_border_distance
            self.paddle_y = self.game.screen_height // 2 - self.paddle_height // 2
        elif self.position == PlayerPosition.RIGHT:
            self.paddle_x = self.game.screen_width - self.paddle_width - \
                self.game.paddle_border_distance
            self.paddle_y =  self.game.screen_height // 2 - self.paddle_height // 2
        elif self.position == PlayerPosition.BOTTOM:
            self.paddle_x = self.game.screen_width // 2 - self.paddle_width // 2
            self.paddle_y = self.game.screen_height - self.paddle_height - \
                self.game.paddle_border_distance
        elif self.position == PlayerPosition.UP:
            self.paddle_x = self.game.screen_width // 2 - self.paddle_width // 2
            self.paddle_y = self.game.paddle_border_distance
        
#------------------------------CONDITION-------------------------------------

    def check_win(self):
        return self.score >= self.game.score_limit

#------------------------------REDIS-------------------------------------

    async def set_data_to_redis(self):
        await self.set_paddle_to_redis(self.paddle_x, "paddle_x")
        await self.set_paddle_to_redis(self.paddle_y, "paddle_y")
        await self.set_score_to_redis(self.score)
        
    async def update_score(self):
        self.score += 1
        await self.set_score_to_redis(self.score)

    async def set_username_to_redis(self, username):
        key = self.key_map["username"]
        await self.redis_ops.set_dynamic_value(key, username)

    async def set_score_to_redis(self, score):
        key = self.key_map["score"]
        await self.redis_ops.set_dynamic_value(key, score)

    async def set_paddle_to_redis(self, new_position, paddle_key):
        key = self.key_map[paddle_key]
        await self.redis_ops.set_dynamic_value(key, new_position)

    async def get_paddle_from_redis(self):
        position_key = "paddle_y" if self.position in [PlayerPosition.LEFT, PlayerPosition.RIGHT] else "paddle_x"
        key = self.key_map[position_key]
        
        paddle_position_str = await self.redis_ops.get_dynamic_value(key)
        paddle_position = int(paddle_position_str)
        
        if position_key == "paddle_y":
            self.paddle_y = paddle_position
        else:
            self.paddle_x = paddle_position
        self.dynamic_pos = paddle_position

#------------------------------COMPACTED DATA-------------------------------------
            
    def get_dynamic_compacted_player_data(self):
        return self.dynamic_pos