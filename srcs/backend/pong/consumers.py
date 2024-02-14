import json
import random
import asyncio
import time

from .game_config import *
from .models import Player, Game, BallCoordinates

from asyncio import sleep
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404

class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialize_game()

#-------------------------------CLASS INITIALIZATION--------------------------------

    def initialize_game(self):
        # static variable
        self.paddle_width = PADDLE_WIDTH
        self.paddle_height = PADDLE_HEIGHT 
        self.paddle_speed = PADDLE_SPEED
        self.ball_speed_range = BALL_SPEED_RANGE
        self.ball_size = BALL_SIZE
        self.canvas_height = SCREEN_HEIGHT
        self.canvas_width = SCREEN_WIDTH
        self.left_player_score = self.right_player_score = INITIAL_SCORE
        self.score_limit = SCORE_LIMIT

        # dynamic variable
        self.ball_launched = False
        self.last_update_time = time.time()
        self.match_over = False
        self.left_paddle = {'up': False, 'down': False, 'y': INITIAL_PADDLE_Y}
        self.right_paddle = {'up': False, 'down': False, 'y': INITIAL_PADDLE_Y}
        self.ball = {
            'x': INITIAL_BALL_X,
            'y': INITIAL_BALL_Y,
            'speedX': random.choice([-self.ball_speed_range, self.ball_speed_range]),
            'speedY': random.choice([-self.ball_speed_range, self.ball_speed_range]),
        }

#-------------------------------WEBSOCKET CONNECTION-------------------------

    async def connect(self):
        await self.accept()

        game_init_data = {
            'type': 'game.init',
            'paddleWidth': self.paddle_width,
            'paddleHeight': self.paddle_height,
            'ballSize': self.ball_size,
            'initialLeftPaddleY': self.left_paddle['y'],
            'initialRightPaddleY': self.right_paddle['y'],
            'initialBallPosition': self.ball,
            'initialLeftPlayerScore': self.left_player_score,
            'initialRightPlayerScore': self.right_player_score,
            'matchOver': self.match_over,
        }

        # Send the game initialization data to the frontend
        await self.send(json.dumps(game_init_data))

        # Start the game loop
        self.ball_launched = True
        asyncio.create_task(self.game_loop())

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)

        delta_time = 0.0

        if data['message'] == 'paddle_movement':
            await self.handle_paddle_movement(data, delta_time)
        else:
            await self.handle_game_update(delta_time, data)

#-------------------------------GAME LOOP-----------------------------------

    async def game_loop(self):
        last_update_time = time.time()

        while True:
            current_time = time.time()
            delta_time = current_time - last_update_time

            # Print delta time for debugging
            # print("Delta Time:", delta_time)

            # Update ball position based on game mechanics
            self.update_ball_position(delta_time)

            # Example: Echo the updated positions back to all clients
            await self.send_game_update(delta_time)

            # Calculate the sleep duration to achieve 60 FPS
            target_fps = 60
            target_frame_time = 1.0 / target_fps
            sleep_duration = max(0, target_frame_time - delta_time)

            # Adjust the sleep duration based on the delta time
            await asyncio.sleep(sleep_duration)

            last_update_time = current_time


    async def send_game_update(self, delta_time=0.0):
        await self.handle_game_update(delta_time)

#-------------------------------PADLLE MOVEMENT-----------------------------

    async def handle_paddle_movement(self, data, delta_time):
        left_paddle_state = data['leftPaddleState']
        right_paddle_state = data['rightPaddleState']

        self.update_paddle_position(self.left_paddle, left_paddle_state)
        self.update_paddle_position(self.right_paddle, right_paddle_state)
        
        self.ball_launched = True
        await self.send_game_update(delta_time)

    def update_paddle_position(self, paddle_movement, paddle_state):
        # Update movement flags based on paddle state
        paddle_movement['up'] = paddle_state['up']
        paddle_movement['down'] = paddle_state['down']

        # Update paddle position based on movement flags
        if paddle_movement['up']:
            paddle_movement['y'] = max(0, paddle_movement['y'] - self.paddle_speed)
        elif paddle_movement['down']:
            paddle_movement['y'] = min(400 - self.paddle_height, paddle_movement['y'] + self.paddle_speed)

#-------------------------------GAME UPDATE-----------------------------
        
    async def handle_game_update(self, delta_time, data=None):
        self.update_ball_position(delta_time)
        await self.send(text_data=json.dumps({
            'type': 'game.update',
            'leftPaddleY': self.left_paddle['y'],
            'rightPaddleY': self.right_paddle['y'],
            'ball': self.ball,
            'leftPlayerScore': self.left_player_score,
            'rightPlayerScore': self.right_player_score,
            'matchOver': self.match_over,
        }))

    def update_ball_position(self, delta_time):
        if not self.ball_launched or self.match_over:
            return

        # Update ball's position based on its speed and direction
        self.ball['x'] += self.ball['speedX'] * delta_time
        self.ball['y'] += self.ball['speedY'] * delta_time

        self.check_collisions()
        self.check_scoring()


#-------------------------------GAME MECHANICS-----------------------------------

    def check_collisions(self):
        # Check for collisions with paddles
        if (
            (self.ball['x'] - self.ball_size/2 < self.paddle_width and
             self.left_paddle['y'] - self.ball_size/2 < self.ball['y'] < self.left_paddle['y'] + self.paddle_height + self.ball_size/2) or
            (self.ball['x'] + self.ball_size/2 > self.canvas_width - self.paddle_width and
             self.right_paddle['y'] - self.ball_size/2 < self.ball['y'] < self.right_paddle['y'] + self.paddle_height + self.ball_size/2)
        ):
            self.handle_paddle_collision()

        # Check for collisions with walls
        if (
            self.ball['y'] - self.ball_size/2 < 0 or
            self.ball['y'] + self.ball_size/2 > self.canvas_height
        ):
            self.handle_wall_collision()

    def handle_paddle_collision(self):
        self.ball['speedX'] *= -1

    def handle_wall_collision(self):
        self.ball['speedY'] *= -1

#-------------------------------GAME STATE-----------------------------------

    def check_scoring(self):
        # Check for scoring (ball crossing left or right border)
        if self.ball['x'] < 0 - self.ball_size/2:
            self.score_for_right_player()
        elif self.ball['x'] > self.canvas_width + self.ball_size/2:
            self.score_for_left_player()

    def score_for_left_player(self):
        self.left_player_score += 1
        self.check_game_over()

    def score_for_right_player(self):
        self.right_player_score += 1
        self.check_game_over()

    def check_game_over(self):
        # Check if any player has reached the maximum score (10)
        if self.left_player_score == self.score_limit or self.right_player_score == self.score_limit:
            # Set match_over to True
            self.match_over = True
        else:
            # Continue the game
            self.reset_ball()

    def reset_ball(self):
        # Set the ball to the initial position and choose a new random speed
        self.ball = {
            'x': INITIAL_BALL_X,
            'y': INITIAL_BALL_Y,
            'speedX': random.choice([-self.ball_speed_range, self.ball_speed_range]),
            'speedY': random.choice([-self.ball_speed_range, self.ball_speed_range]),
        }

        # Stop the ball temporarily
        self.ball_launched = False

        # Wait for a moment before launching the ball again
        sleep(10)

        # Launch the ball
        self.ball_launched = True