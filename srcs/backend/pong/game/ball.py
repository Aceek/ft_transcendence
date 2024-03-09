import math

from .enum import PlayerPosition
from .utils import calculate_launch_angle, generate_adjusted_random_speed

class Ball:
    def __init__(self, game):
        self.game = game  
        self.redis_ops = game.redis_ops
        self.size = game.ball_size
        self.reset_value()


    def reset_value(self):
        self.x = int(self.game.screen_width / 2)
        self.y = int(self.game.screen_height / 2)
        
        speed = generate_adjusted_random_speed(self.game.ball_speed, 15)
        angle_rad = calculate_launch_angle(self.game.player_nb, 60)

        # Calculate the velocity components based on the angle
        self.vx = speed * math.cos(angle_rad)
        self.vy = speed * math.sin(angle_rad)

        self.lastPlayerTouched = None

    async def set_data_to_redis(self):
        await self.set_ball_to_redis()

    def update_position(self, delta_time):
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time

#------------------------------CONDITION-------------------------------------

    def check_wall_collision(self):
        if self.game.player_nb == 4:
            return False
        elif self.game.player_nb == 3:
            if self.y - self.size / 2 < 0:
                return True
        else:
            if (self.y - self.size / 2 < 0 or
                    self.y + self.size / 2 > self.game.screen_height):
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
                    if player.position == PlayerPosition.LEFT or player.position == PlayerPosition.RIGHT:
                        self.vx *= -1
                    elif player.position == PlayerPosition.BOTTOM or player.position == PlayerPosition.UP:
                        self.vy *= -1
                    return True
            return False

        for player in players:
            if detect_collision_and_handle_edge_bounce(player):
                self.lastPlayerTouched = player
                return True, player
                    
        return False, None

    def check_score(self):     
        # Normal check for a game of 2 players
        if self.game.player_nb <= 2:        
            if self.x < 0 - self.size / 2:
                # Find and return the player object for PlayerPosition.RIGHT
                return True, next((player for player in self.game.players if player.position == PlayerPosition.RIGHT), None)
            elif self.x > self.game.screen_width + self.size / 2:
                # Find and return the player object for PlayerPosition.LEFT
                return True, next((player for player in self.game.players if player.position == PlayerPosition.LEFT), None)
        else:
            # Custom check for a game of more than 2 players
            # Allowing the goal to the last player who touched the ball
            if self.x < 0 - self.size / 2 or \
            self.x > self.game.screen_width + self.size / 2 or \
            self.y < 0 - self.size / 2 or \
            self.y < 0 - self.size / 2 or \
            self.y > self.game.screen_height + self.size / 2:
                return True, self.lastPlayerTouched

        return False, None

#------------------------------HANDLER-------------------------------------

    def handle_wall_bounce(self):
        self.vy *= -1
        self.y = max(self.size / 2, min(self.y, self.game.screen_height - self.size / 2))
        
    def handle_paddle_bounce_calculation(self, player):
        position = player.position
        paddle_x = player.paddle_x
        paddle_y = player.paddle_y
        paddle_width = player.paddle_width
        paddle_height = player.paddle_height

        # Adjust calculations based on player position
        if position == PlayerPosition.LEFT:
            relative_position = (self.y - self.size / 2 - paddle_y) / paddle_height
        elif position == PlayerPosition.RIGHT:
            relative_position = (self.y + self.size / 2 - paddle_y) / paddle_height
        elif position == PlayerPosition.UP:
            relative_position = (self.x - self.size / 2 - paddle_x) / paddle_width
        elif position == PlayerPosition.BOTTOM:
            relative_position = (self.x + self.size / 2 - paddle_x) / paddle_width
        angle = (relative_position - 0.5) * math.pi / 2 

        # Calculate speed based on the current velocity
        speed = math.sqrt(self.vx**2 + self.vy**2)

        # Adjust velocity based on the collision with the paddle
        if position == PlayerPosition.LEFT:
            self.vx = speed * math.cos(angle)
            self.vy = speed * math.sin(angle)
        elif position == PlayerPosition.RIGHT:
            self.vx = speed * math.cos(angle) *-1
            self.vy = speed * math.sin(angle)
        elif position == PlayerPosition.BOTTOM:
            self.vx = speed * math.sin(angle)
            self.vy = speed * math.cos(angle) * -1
        elif position == PlayerPosition.UP:
            self.vx = speed * math.sin(angle)
            self.vy = speed * math.cos(angle)

        # print(f"Bounce detected! Ball Position: ({self.x}, {self.y}), Relative Position: {relative_position}, Angle: {angle} radians")

#------------------------------REDIS-------------------------------------

    async def set_ball_to_redis(self):
        ball_attributes = {
            'b_x': round(self.x, 2),
            'b_y': round(self.y, 2),
            'b_vx': round(self.vx, 2),
            'b_vy': round(self.vy, 2)
        }
        await self.redis_ops.set_dynamic_data(ball_attributes)

#------------------------------COMPACTED DATA-------------------------------------

    def get_dynamic_compacted_ball_data(self):
        return [round(self.x, 2),\
                round(self.y, 2),\
                round(self.vx, 2),\
                round(self.vy, 2)]
