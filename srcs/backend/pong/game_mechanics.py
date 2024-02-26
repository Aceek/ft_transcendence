import math
import random

from .game_config import *

def update_ball(ball, players, delta_time):
    # Calculate the next position of the ball
    next_x = ball["x"] + ball["vx"] * delta_time
    next_y = ball["y"] + ball["vy"] * delta_time

    # Create a new ball object with the next position
    next_ball = {
        "x": next_x,
        "y": next_y,
        "vx": ball["vx"],  # Preserving the current speed
        "vy": ball["vy"]
    }

    # Check and handle wall collision
    if check_wall_collision(next_ball):
        next_ball = handle_wall_collision(next_ball)

    # Check and handle paddle collision
    elif check_paddle_collisons(next_ball, players):
        next_ball = handle_paddle_collision(next_ball, players)
    
    scored, side = check_score(next_ball, players)
    if scored:
        players[side]["score"]["value"] += 1
        players[side]["score"]["updated"] = True
        next_ball = {
            "x": INITIAL_BALL_X,
            "y": INITIAL_BALL_Y,
            "vx": random.choice([-BALL_SPEED_RANGE, BALL_SPEED_RANGE]),
            "vy": random.choice([-BALL_SPEED_RANGE, BALL_SPEED_RANGE]),
        }

    return next_ball, players

    # check_scoring()

def check_wall_collision(next_ball):
    # Check for wall collisions based on predicted position
    if (
        next_ball["y"] - BALL_SIZE / 2 < 0
        or next_ball["y"] + BALL_SIZE / 2 > SCREEN_HEIGHT
    ):
        return True
    return False

def check_paddle_collisons(next_ball, players):
    # Check for collisions with paddles
    if (
        next_ball["x"] - BALL_SIZE / 2 < PADDLE_WIDTH
        and players["left"]["paddle"]["y"]
        < next_ball["y"]
        < players["left"]["paddle"]["y"]  + PADDLE_HEIGHT
    ) or (
        next_ball["x"] + BALL_SIZE / 2 > SCREEN_WIDTH - PADDLE_WIDTH
        and players["right"]["paddle"]["y"]
        < next_ball["y"]
        < players["right"]["paddle"]["y"]  + PADDLE_HEIGHT
    ):
        return True
    return False

def handle_paddle_collision(next_ball, players):
    # Determine which paddle was hit
    if next_ball["x"] < SCREEN_WIDTH / 2:
        paddle = players["left"]["paddle"]
        direction = 1
    else:
        paddle = players["right"]["paddle"]
        direction = -1

    # Calculate the relative position of the collision point on the paddle
    relative_collision_position = (
        next_ball["y"] - paddle["y"]
    ) / PADDLE_HEIGHT

    # Calculate the new angle of the ball's trajectory based on the relative position
    angle = (relative_collision_position - 0.5) * math.pi / 2

    # Update the ball's speed components based on the new angle
    speed_magnitude = math.sqrt(next_ball["vx"] ** 2 + next_ball["vy"] ** 2)
    next_ball["vx"] = speed_magnitude * math.cos(angle) * direction
    next_ball["vy"] = speed_magnitude * math.sin(angle) * direction
    return next_ball

def handle_wall_collision(next_ball):
    adjusted_y = max(BALL_SIZE / 2, min(next_ball["y"], SCREEN_HEIGHT - BALL_SIZE / 2))
    next_ball["y"] = adjusted_y
    next_ball["vy"] *= -1
    return next_ball

def check_score(ball, players):
    if ball["x"] < 0 - BALL_SIZE / 2:
        return True, "right"
    elif ball["x"] > SCREEN_WIDTH + BALL_SIZE / 2:
        return True, "left"
    
    return False, None