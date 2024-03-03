import random
import math

from .config import *
from .enum import PlayerPosition
from .utils import calculate_launch_angle

class Ball:
    def __init__(self, redis_ops):
        self.reset_value()
        self.redis_ops = redis_ops
        
        self.size = BALL_SIZE

    def reset_value(self):
        self.x = BALL_X
        self.y = BALL_Y
        
        speed = BALL_SPEED_RANGE

        angle_rad = calculate_launch_angle(PLAYER_NB, 60)

        # Calculate the velocity components based on the angle
        self.vx = speed * math.cos(angle_rad)
        self.vy = speed * math.sin(angle_rad)

        self.lastPlayertouched = None

    async def set_data_to_redis(self):
        await self.set_ball_to_redis()

    def update_position(self, delta_time):
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time

#------------------------------CONDITION-------------------------------------

    def check_wall_collision(self):
        if PLAYER_NB == 4:
            return False
        elif PLAYER_NB == 3:
            if self.y - self.size / 2 < 0:
                return True
        else:
            if (self.y - self.size / 2 < 0 or
                    self.y + self.size / 2 > SCREEN_HEIGHT):
                return True
        return False

    def check_paddle_collision(self, players):
        def detect_collision_and_handle_edge_bounce(player):
            # Access the player's paddle attributes directly
            paddle_x, paddle_y = player.paddle_x, player.paddle_y
            paddle_width, paddle_height = player.paddle_width, player.paddle_height

            # Check for horizontal overlap
            if paddle_x <= self.x - self.size / 2 <= paddle_x + paddle_width or \
                paddle_x <= self.x + self.size / 2 <= paddle_x + paddle_width:
                # Check for vertical overlap
                if paddle_y <= self.y - self.size / 2 <= paddle_y + paddle_height or \
                    paddle_y <= self.y + self.size / 2 <= paddle_y + paddle_height:
                    if player.side == PlayerPosition.LEFT or player.side == PlayerPosition.RIGHT:
                        self.vx *= -1
                    elif player.side == PlayerPosition.BOTTOM or player.side == PlayerPosition.UP:
                        self.vy *= -1
                    return True
            return False

        for player in players:
            if detect_collision_and_handle_edge_bounce(player):
                self.lastPlayertouched = player.side
                return True, player.side
                    
        return False, None

    def check_score(self):     
        # Normal check for game of 2 players
        if PLAYER_NB <=2:        
            if self.x < 0 - self.size / 2:
                return True, PlayerPosition.RIGHT
            elif self.x > SCREEN_WIDTH + self.size / 2:
                return True, PlayerPosition.LEFT
        else:
            # Custum check for game of more then 2 players
            # allowing the goal to the last player who touched the ball
            if self.x < 0 - self.size / 2 or \
            self.x > SCREEN_WIDTH + self.size / 2 or \
            self.y < 0 - self.size / 2 or \
            self.y < 0 - self.size / 2 or \
            self.y > SCREEN_HEIGHT + self.size / 2:
                return True, self.lastPlayertouched

        return False, None

#------------------------------HANDLER-------------------------------------

    def handle_wall_bounce(self):
        self.vy *= -1
        self.y = max(self.size / 2, min(self.y, SCREEN_HEIGHT - self.size / 2))
        
    def handle_paddle_bounce_calculation(self, player_position, players):
        player = players[player_position.value]
        paddle_x = player.paddle_x
        paddle_y = player.paddle_y
        paddle_width = player.paddle_width
        paddle_height = player.paddle_height

        # Adjust calculations based on player position
        if player_position == PlayerPosition.LEFT:
            relative_position = (self.y - self.size / 2 - paddle_y) / paddle_height
        elif player_position == PlayerPosition.RIGHT:
            relative_position = (self.y + self.size / 2 - paddle_y) / paddle_height
        elif player_position == PlayerPosition.UP:
            relative_position = (self.x - self.size / 2 - paddle_x) / paddle_width
        elif player_position == PlayerPosition.BOTTOM:
            relative_position = (self.x + self.size / 2 - paddle_x) / paddle_width
        angle = (relative_position - 0.5) * math.pi / 2 

        # Calculate speed based on the current velocity
        speed = math.sqrt(self.vx**2 + self.vy**2)

        # Adjust velocity based on the collision with the paddle
        if player_position == PlayerPosition.LEFT:
            self.vx = speed * math.cos(angle)
            self.vy = speed * math.sin(angle)
        elif player_position == PlayerPosition.RIGHT:
            self.vx = speed * math.cos(angle) *-1
            self.vy = speed * math.sin(angle)
        elif player_position == PlayerPosition.BOTTOM:
            self.vx = speed * math.sin(angle)       # Reflecting horizontally based on the angle
            self.vy = speed * math.cos(angle) * -1  # Negative to move upwards
        elif player_position == PlayerPosition.UP:
            self.vx = speed * math.sin(angle)  # Reflecting horizontally based on the angle
            self.vy = speed * math.cos(angle)

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