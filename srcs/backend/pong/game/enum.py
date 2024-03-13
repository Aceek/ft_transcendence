from enum import Enum

class GameStatus(Enum):
    UNSTARTED = -1
    LAUNCHING = 0
    IN_PROGRESS = 1
    SUSPENDED = 2
    COMPLETED = 3

class PlayerPosition(Enum):
    LEFT = 0
    RIGHT = 1
    BOTTOM = 2
    UP = 3
    SPEC = 4