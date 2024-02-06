# game_logic.py

from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
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
    # Define your game loop logic here
    while True:
        try:

            # Print the updated game state to the terminal
            print('Game State:', game)

            # Optional: Adjust the sleep duration based on your desired frame rate
            time.sleep(1)  # Sleep for 1 second

        except Exception as e:
            print(f'An error occurred in the game loop: {str(e)}')