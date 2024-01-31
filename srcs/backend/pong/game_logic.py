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

        # Initialize ball coordinates for the game
        ball = BallCoordinates.objects.create(game=game)

        # Return JSON data
        return {
            'id': game.id,
            'message': 'Game initialized successfully',
            'screen': {
                'width': SCREEN_WIDTH,
                'height': SCREEN_HEIGHT,
            },
            'paddle': {
                'width': PADDLE_WIDTH,
                'height': PADDLE_HEIGHT,
                'speed':PADDLE_SPEED,
            },
            'ball': {
                'width': BALL_WIDTH,
                'height': BALL_HEIGHT,
                'speed':BALL_SPEED,
                'x': ball.x,
                'y': ball.y,
            },
            'players': [
                {'player_id': player1.player_id, 'score': player1.score, 'paddle_y': player1.paddle_y},
                {'player_id': player2.player_id, 'score': player2.score, 'paddle_y': player2.paddle_y}
            ],
        }, 200
    
    except Player.DoesNotExist:
        return {'error': 'Player not found'}, 404

    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}, 500

