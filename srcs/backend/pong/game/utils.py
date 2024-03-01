from .enum import PlayerPosition
from .config import *

def get_player_key_map(position):
    player_key_map = {
        PlayerPosition.LEFT: {
            "position": "left",
            "score": "lp_s",
            "paddle_y": "lp_y",
            "paddle_x": "lp_x"
        },
        PlayerPosition.RIGHT: {
            "position": "right",
            "score": "rp_s",
            "paddle_y": "rp_y",
            "paddle_x": "rp_x" 
        },
        PlayerPosition.BOTTOM: {
            "position": "bottom",
            "score": "bp_s",
            "paddle_y": "bp_y",
            "paddle_x": "bp_x"
        },
        PlayerPosition.UP: {
            "position": "up",
            "score": "up_s",
            "paddle_y": "up_y",
            "paddle_x": "up_x"
        }
    }

    return player_key_map.get(position)

