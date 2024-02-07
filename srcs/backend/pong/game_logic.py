# game_logic.py

from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from .game_config import *
import random
import time

def initialize_game(player1_id, player2_id):
    try:
        # Retrieve player objects from the database
        player1 = get_object_or_404(Player, player_id=player1_id)
        player2 = get_object_or_404(Player, player_id=player2_id)

        # Create a new game
        game = Game.objects.create(player1_id=player1_id, player2_id=player2_id)

        # Initialize ball coordinates for the game
        ball = BallCoordinates.objects.create(game=game)

        # Serialize the game data
        game_serializer = GameSerializer(game)

        # Return the serialized data
        return game_serializer.data, 200
    
    except Player.DoesNotExist:
        return {'error': 'Player not found'}, 404

    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}, 500

def start_game(game):
        # Set the initial state of the game (you may customize this based on your game logic)
        # set_initial_game_state(game)

        # Start the game loop
        start_game_loop(game)

def start_game_loop(game):
    # Define a variable to keep track of time for saving to the database
    last_save_time = time.time()

    # Define your game loop logic here
    while True:
        try:
            # Fetch the existing ball coordinates object associated with the game
            ball_coordinates = game.ball_coordinates

            # Move the ball
            ball_coordinates.x += ball_coordinates.speed_x
            ball_coordinates.y += ball_coordinates.speed_y

            # Check for collisions with walls
            if ball_coordinates.y <= 0 or ball_coordinates.y >= SCREEN_HEIGHT:
                ball_coordinates.speed_y *= -1  # Reverse the vertical direction if hitting the top or bottom wall

            # Check if the ball goes beyond either side of the screen
            if ball_coordinates.x <= 0 or ball_coordinates.x >= SCREEN_WIDTH:
                # Respawn the ball at a random position on the left side of the screen
                ball_coordinates.x = random.randint(0, SCREEN_WIDTH // 2 - BALL_WIDTH)  # Adjust range for left side
                ball_coordinates.y = random.randint(0, SCREEN_HEIGHT - BALL_HEIGHT)

            # Save ball coordinates to the database every 100 milliseconds
            current_time = time.time()
            if current_time - last_save_time >= 0.1:  # 0.1 seconds = 100 milliseconds
                # Save the updated ball coordinates to the database
                ball_coordinates.save()
                # Update the last save time
                last_save_time = current_time

            # Optional: Adjust the sleep duration based on your desired frame rate
            time.sleep(0.1)  # Sleep for 0.1 second (adjust as needed)

        except Exception as e:
            print(f'An error occurred in the game loop: {str(e)}')
