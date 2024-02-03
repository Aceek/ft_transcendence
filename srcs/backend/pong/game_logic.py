# game_logic.py

from .models import *
from .serializers import *
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

        # Serialize the game data
        game_serializer = GameSerializer(game)

        # Return the serialized data
        return game_serializer.data, 200
    
    except Player.DoesNotExist:
        return {'error': 'Player not found'}, 404

    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}, 500

