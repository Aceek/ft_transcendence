from .config import *
from .ball import Ball
from .player import Player


def update_ball(ball, players, delta_time):
    # Calculate the next position of the ball
    ball.update_position(delta_time)

    # Check and handle wall collision
    if ball.check_wall_collision():
        ball.handle_wall_collision()

    # Check and handle paddle collision
    collision, position = ball.check_paddle_collision(players)
    if collision:
        ball.handle_paddle_collision(position, players)
    
    scored, scorer_position = ball.check_score()
    if scored:
        players[scorer_position.value].update_score()
        ball.reset_value()