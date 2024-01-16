import json
import random
import asyncio
import time
from asyncio import sleep
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialize_game()

    def initialize_game(self):
        # Initialize game parameters
        self.paddle_width = 10
        self.paddle_height = 80 
        self.left_paddle_y = self.right_paddle_y = 160
        self.paddle_speed = 16
        self.ball_speed_range = 50
        self.ball_size = 10
        self.canvas_height = 400
        self.canvas_width = 800
        self.ball_launched = False
        self.last_update_time = time.time()
        self.left_player_score = 0
        self.right_player_score = 0
        self.match_over = False

        # Initialize ball position and speed
        self.ball_position = {
            'x': 400,
            'y': 300,
            'speedX': random.choice([-self.ball_speed_range, self.ball_speed_range]),
            'speedY': random.choice([-self.ball_speed_range, self.ball_speed_range]),
        }

    async def connect(self):
        await self.accept()
        self.ball_launched = True
        asyncio.create_task(self.game_loop())

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Received message: {text_data}")

        delta_time = 0.0

        if data['message'] == 'paddle_movement':
            await self.handle_paddle_movement(data, delta_time)
        else:
            await self.handle_game_update(delta_time, data)

    async def game_loop(self):
        last_update_time = time.time()

        while True:
            current_time = time.time()
            delta_time = current_time - last_update_time

            # Update ball position based on game mechanics
            self.update_ball_position(delta_time)

            # Example: Echo the updated positions back to all clients
            await self.send_game_update(delta_time)

            # Adjust the sleep duration based on the delta time
            await asyncio.sleep(0.002 - delta_time)  # 240 FPS target

            last_update_time = current_time

    async def handle_paddle_movement(self, data, delta_time):
        key, is_pressed = data['key'], data['isPressed']
        self.update_paddle_positions(key, is_pressed)
        self.ball_launched = True
        await self.send_game_update(delta_time)

    def update_paddle_positions(self, key, is_pressed):
        # Update paddle coordinates based on key and is_pressed
        update_left_paddle = key == 'w' or key == 's'
        update_right_paddle = key == 'ArrowUp' or key == 'ArrowDown'

        if update_left_paddle:
            self.left_paddle_y = max(0, min(320, self.left_paddle_y + (-1 if key == 'w' else 1) * self.paddle_speed))
        elif update_right_paddle:
            self.right_paddle_y = max(0, min(320, self.right_paddle_y + (-1 if key == 'ArrowUp' else 1) * self.paddle_speed))

    async def update_game_state(self):
        delta_time = time.time() - self.last_update_time
        self.last_update_time = time.time()
        self.update_ball_position(delta_time)
        await asyncio.sleep(0)

    async def send_game_update(self, delta_time=0.0):
        await self.handle_game_update(delta_time)

    def update_ball_position(self, delta_time):
        if not self.ball_launched:
            return

        # Update ball's position based on its speed and direction
        self.ball_position['x'] += self.ball_position['speedX'] * delta_time
        self.ball_position['y'] += self.ball_position['speedY'] * delta_time

        self.check_collisions()
        self.check_scoring()

    def check_collisions(self):
        # Check for collisions with paddles
        if (
            (self.ball_position['x'] - self.ball_size/2 < self.paddle_width and
             self.left_paddle_y < self.ball_position['y'] < self.left_paddle_y + self.paddle_height) or
            (self.ball_position['x'] + self.ball_size/2 > self.canvas_width - self.paddle_width and
             self.right_paddle_y < self.ball_position['y'] < self.right_paddle_y + self.paddle_height)
        ):
            self.handle_paddle_collision()

        # Check for collisions with walls
        if (
            self.ball_position['y'] - self.ball_size/2 < 0 or
            self.ball_position['y'] + self.ball_size/2 > self.canvas_height
        ):
            self.handle_wall_collision()

    def check_scoring(self):
        # Check for scoring (ball crossing left or right border)
        if self.ball_position['x'] < 0 - self.ball_size/2:
            self.score_for_right_player()
            self.reset_ball()
        elif self.ball_position['x'] > self.canvas_width + self.ball_size/2:
            self.score_for_left_player()
            self.reset_ball()

    def handle_paddle_collision(self):
        self.ball_position['speedX'] *= -1

    def handle_wall_collision(self):
        self.ball_position['speedY'] *= -1

    async def handle_game_update(self, delta_time, data=None):
        self.update_ball_position(delta_time)
        await self.send(text_data=json.dumps({
            'type': 'game.update',
            'leftPaddleY': self.left_paddle_y,
            'rightPaddleY': self.right_paddle_y,
            'ballPosition': self.ball_position,
            'leftPlayerScore': self.left_player_score,
            'rightPlayerScore': self.right_player_score,
            'matchOver': self.match_over,
        }))

    def score_for_left_player(self):
        self.left_player_score += 1
        self.check_game_over()

    def score_for_right_player(self):
        self.right_player_score += 1
        self.check_game_over()

    def check_game_over(self):
        # Check if any player has reached the maximum score (10)
        if self.left_player_score == 10 or self.right_player_score == 10:
            # Reset scores and restart the game
            self.left_player_score = self.right_player_score = 0
            self.match_over = True
        else:
            # Continue the game
            self.reset_ball()

    def reset_ball(self):
        # Set the ball to the initial position and choose a new random speed
        self.ball_position = {
            'x': 400,
            'y': 300,
            'speedX': random.choice([-self.ball_speed_range, self.ball_speed_range]),
            'speedY': random.choice([-self.ball_speed_range, self.ball_speed_range]),
        }

        # Stop the ball temporarily
        self.ball_launched = False

        # Wait for a moment before launching the ball again
        sleep(10)

        # Launch the ball
        self.ball_launched = True
