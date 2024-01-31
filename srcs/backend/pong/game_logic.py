# game_logic.py

from .models import *
from .game_config import *
from django.shortcuts import get_object_or_404

def initialize_game(player1_id, player2_id):
    try:
        # Retrieve player objects from the database
        player1 = get_object_or_404(Player, player_id=player1_id)
        player2 = get_object_or_404(Player, player_id=player2_id)
        
        # Create a new game
        game = Game.objects.create(player1_id=player1_id, player2_id=player2_id)

        # Initialize paddle coordinates for player 1 and player 2
        paddle1 = PaddleCoordinates.objects.create(game=game, player=player1)
        paddle2 = PaddleCoordinates.objects.create(game=game, player=player2)

        # Initialize ball coordinates for the game
        ball = BallCoordinates.objects.create(game=game)

        # Return JSON data
        return {
            'game_id': game.id,
            'message': 'Game initialized successfully',
            'players': [
                {'player_id': player1.player_id, 'score': player1.score},
                {'player_id': player2.player_id, 'score': player2.score}
            ],
            'paddle_coordinates': [
                {'player_id': player1.player_id, 'paddle_y': paddle1.paddle_y},
                {'player_id': player2.player_id, 'paddle_y': paddle2.paddle_y}
            ],
            'ball_position': {'x_position': ball.x_position, 'y_position': ball.y_position}
        }, 200

    except Player.DoesNotExist:
        return {'error': 'Player not found'}, 404

    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}, 500

