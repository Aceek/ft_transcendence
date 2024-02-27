from enum import Enum

class GameStatus(Enum):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    SUSPENDED = 2
    COMPLETED = 3
