# # pong/views.py
# import json
# import random
# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import Paddle, Ball, Game

# def pong_game(request):
#     # Retrieve or create game instance
#     game, created = Game.objects.get_or_create(id=1)

#     # Retrieve or create paddle instances
#     left_paddle, created = Paddle.objects.get_or_create(player='left', game=game)
#     right_paddle, created = Paddle.objects.get_or_create(player='right', game=game)

#     # Retrieve or create ball instance
#     ball, created = Ball.objects.get_or_create(game=game)

#     # Perform game logic (update paddle and ball positions, check collisions, etc.)
#     delta_time = 0.002  # Adjust the delta_time based on your game loop timing
#     update_ball_position(ball, delta_time, game)

#     # Return game state as JSON response
#     game_state = {
#         'leftPaddleY': left_paddle.y,
#         'rightPaddleY': right_paddle.y,
#         'ballPosition': {'x': ball.x, 'y': ball.y},
#         'leftPlayerScore': game.left_player_score,
#         'rightPlayerScore': game.right_player_score,
#         'matchOver': game.match_over,
#     }

#     return JsonResponse(game_state)

# def update_ball_position(ball, delta_time, game):
#     if not game.ball_launched or game.match_over:
#         return

#     # Update ball's position based on its speed and direction
#     ball.x += ball.speed_x * delta_time
#     ball.y += ball.speed_y * delta_time

#     check_collisions(ball, game)
#     check_scoring(ball, game)

# def check_collisions(ball, game):
#     # Check for collisions with paddles
#     if (
#         (ball.x - ball.size/2 < game.paddle_width and
#          game.left_paddle_y < ball.y < game.left_paddle_y + game.paddle_height) or
#         (ball.x + ball.size/2 > game.canvas_width - game.paddle_width and
#          game.right_paddle_y < ball.y < game.right_paddle_y + game.paddle_height)
#     ):
#         handle_paddle_collision(ball)

#     # Check for collisions with walls
#     if (
#         ball.y - ball.size/2 < 0 or
#         ball.y + ball.size/2 > game.canvas_height
#     ):
#         handle_wall_collision(ball)

# def check_scoring(ball, game):
#     # Check for scoring (ball crossing left or right border)
#     if ball.x < 0 - ball.size/2:
#         score_for_right_player(game)
#     elif ball.x > game.canvas_width + ball.size/2:
#         score_for_left_player(game)

# def handle_paddle_collision(ball):
#     ball.speed_x *= -1

# def handle_wall_collision(ball):
#     ball.speed_y *= -1

# def handle_game_update(ball, game):
#     update_ball_position(ball, 0.002, game)
#     return {
#         'leftPaddleY': game.left_paddle_y,
#         'rightPaddleY': game.right_paddle_y,
#         'ballPosition': {'x': ball.x, 'y': ball.y},
#         'leftPlayerScore': game.left_player_score,
#         'rightPlayerScore': game.right_player_score,
#         'matchOver': game.match_over,
#     }

# def score_for_left_player(game):
#     game.left_player_score += 1
#     check_game_over(game)

# def score_for_right_player(game):
#     game.right_player_score += 1
#     check_game_over(game)

# def check_game_over(game):
#     # Check if any player has reached the maximum score (10)
#     if game.left_player_score == game.score_limit or game.right_player_score == game.score_limit:
#         # Set match_over to True
#         game.match_over = True
#     else:
#         # Continue the game
#         reset_ball(game)

# def reset_ball(game):
#     # Set the ball to the initial position and choose a new random speed
#     game.ball_position = {
#         'x': 400,
#         'y': 300,
#         'speedX': random.choice([-game.ball_speed_range, game.ball_speed_range]),
#         'speedY': random.choice([-game.ball_speed_range, game.ball_speed_range]),
#     }

#     # Stop the ball temporarily
#     game.ball_launched = False

#     # Wait for a moment before launching the ball again
#     sleep(10)

#     # Launch the ball
#     game.ball_launched = True
