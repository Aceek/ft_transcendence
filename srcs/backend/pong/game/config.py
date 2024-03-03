#GAME
PLAYER_NB = 2

#SCREEN
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

if PLAYER_NB > 2:
    SCREEN_WIDTH = SCREEN_HEIGHT

#PADDLE
PADDLE_HEIGHT = int(SCREEN_HEIGHT * 0.2)
PADDLE_WIDTH = int(SCREEN_HEIGHT * 0.02)
PADDLE_BORDER_DISTANCE = int(SCREEN_HEIGHT * 0.04)
PADDLE_SPEED = 10

#BALL
BALL_X = int(SCREEN_WIDTH * 0.5)
BALL_Y = int(SCREEN_HEIGHT * 0.5)
BALL_SIZE = int(SCREEN_HEIGHT *0.02)
BALL_SPEED_RANGE = 50

#SCORE
SCORE_START = 0
SCORE_LIMIT = 3

#NETWORK
TICK_RATE = 60