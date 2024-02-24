from enum import Enum

class GameStatus(Enum):
    NOT_STARTED = 0
    WAITING_PLAYERS = 1
    IN_PROGRESS = 2
    SUSPENDED = 3
    COMPLETED = 4
