from .game_config import *

def check_scoring(ball, players):
    # Determine which side the ball is on and update scoring
    if ball["x"] < 0 - BALL_SIZE / 2:
        scorer = "left"
    elif ball["x"] > SCREEN_WIDTH + BALL_SIZE / 2:
        scorer = "right"
    else:
        return False, players  # No scoring occurred

    # Update the score for the determined side
    players[scorer]["score"]["value"] += 1
    players[scorer]["score"]["updated"] = True
    return True, players

def check_game_over(players):
    if (
        players["left"]["score"]["value"] >= SCORE_LIMIT
        or players["right"]["score"]["value"] >= SCORE_LIMIT
    ):
        return True
    return False