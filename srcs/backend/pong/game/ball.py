import random
import math

from .config import *
from .enum import PlayerPosition

class Ball:
    def __init__(self, redis_ops):
        self.reset_value()
        self.redis_ops = redis_ops

    def reset_value(self):
        self.x = INITIAL_BALL_X
        self.y = INITIAL_BALL_Y
        self.vx = random.choice([-BALL_SPEED_RANGE, BALL_SPEED_RANGE])
        self.vy = random.choice([-BALL_SPEED_RANGE, BALL_SPEED_RANGE])

    async def set_data_to_redis(self):
        await self.set_ball_to_redis()

    def update_position(self, delta_time):
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time

#------------------------------CONDITION-------------------------------------

    def check_wall_collision(self):
        if (
           self.y - BALL_SIZE / 2 < 0
            or self.y + BALL_SIZE / 2 > SCREEN_HEIGHT
        ):
            return True
        return False

    def check_paddle_collision(self, players):
        def detect_collision_and_handle_edge_bounce(paddle_x, paddle_y):
            if paddle_x < self.x < paddle_x + PADDLE_WIDTH + BALL_SIZE:
                if paddle_y <= self.y <= paddle_y + PADDLE_HEIGHT:
                    return True
                elif (abs(self.y - paddle_y) <= BALL_SIZE / 2 or
                    abs(self.y - (paddle_y + PADDLE_HEIGHT)) <= BALL_SIZE / 2):
                    self.vy *= -1  # Reverse y-velocity for edge collision
                    return True
            return False

        for player in players:
            if detect_collision_and_handle_edge_bounce(player.paddle_x, player.paddle_y):
                return True, player.side
                
        return False, None 

    def check_score(self):
        if self.x < 0 - BALL_SIZE / 2:
            return True, PlayerPosition.RIGHT
        elif self.x > SCREEN_WIDTH + BALL_SIZE / 2:
            return True, PlayerPosition.LEFT
        return False, None

#------------------------------HANDLER-------------------------------------

    def handle_wall_bounce(self):
        self.vy *= -1
        self.y = max(BALL_SIZE / 2, min(self.y, SCREEN_HEIGHT - BALL_SIZE / 2))
        
    def handle_paddle_bounce_calculation(self, player_position, players):
        player = players[player_position.value]
        paddle_y = player.paddle_y
        relative_position = (self.y - paddle_y) / PADDLE_HEIGHT
        angle = (relative_position - 0.5) * math.pi / 2

        # Calculate speed based on the current velocity
        speed = math.sqrt(self.vx**2 + self.vy**2)

        # Adjust velocity based on the collision with the paddle
        self.vx = speed * math.cos(angle) * (-1 if player_position == PlayerPosition.RIGHT else 1)
        self.vy = speed * math.sin(angle)

#------------------------------REDIS-------------------------------------

    async def set_ball_to_redis(self):
        # Prepare a dictionary with the ball attributes prefixed by 'b_'
        ball_attributes = {
            'b_x': round(self.x, 8),  # Keep 4 decimal places
            'b_y': round(self.y, 8),
            'b_vx': round(self.vx, 8),
            'b_vy': round(self.vy, 8)
        }
        await self.redis_ops.set_dynamic_data(ball_attributes)