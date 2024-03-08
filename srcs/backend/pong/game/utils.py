import random
import math

from .enum import PlayerPosition
from .config import *

def get_player_key_map(position):
    player_key_map = {
        PlayerPosition.LEFT: {
            "position": "left",
            "username": "lp_u",
            "score": "lp_s",
            "paddle_y": "lp_y",
            "paddle_x": "lp_x"
        },
        PlayerPosition.RIGHT: {
            "position": "right",
            "username": "rp_u",
            "score": "rp_s",
            "paddle_y": "rp_y",
            "paddle_x": "rp_x" 
        },
        PlayerPosition.BOTTOM: {
            "position": "bottom",
            "username": "bp_u",
            "score": "bp_s",
            "paddle_y": "bp_y",
            "paddle_x": "bp_x"
        },
        PlayerPosition.UP: {
            "position": "up",
            "username": "up_u",           
            "score": "up_s",
            "paddle_y": "up_y",
            "paddle_x": "up_x"
        }
    }

    return player_key_map.get(position)

def calculate_launch_angle(player_nb, angle_range):
    player_directions = {
        'left': 180,
        'right': 360,
        'bottom': 270,
        'up': 90
    }

    if player_nb == 2:
        possible_directions = ['left', 'right']
    elif player_nb == 3:
        possible_directions = ['left', 'right', 'bottom']
    elif player_nb == 4:
        possible_directions = ['left', 'right', 'bottom', 'up']

    selected_direction = random.choice(possible_directions)

    central_angle = player_directions[selected_direction]

    angle_deg = random.randint(central_angle % 360 - angle_range//2, \
                                central_angle % 360 + angle_range//2)

    return math.radians(angle_deg)

def generate_adjusted_random_speed(original_speed, range):
    range = range / 100
    adjustment_factor = random.uniform(-range, range)
    adjusted_speed = original_speed * (1 + adjustment_factor)

    return adjusted_speed