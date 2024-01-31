# pong/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from .game_logic import initialize_game

class InitGameView(APIView):
    def post(self, request, *args, **kwargs):
        player1_id = request.data.get('player1_id')
        player2_id = request.data.get('player2_id')

        # Call the initialize_game function to handle game initialization
        result, status_code = initialize_game(player1_id, player2_id)

        # Return the response with the JSON data
        return Response(result, status=status_code)

class PopulateDatabaseView(APIView):
    def post(self, request, *args, **kwargs):
        # Add players to the database
        players_data = [
            {"player_id": "1"},
            {"player_id": "2"},
            # Add more players as needed
        ]

        for player_data in players_data:
            player, created = Player.objects.get_or_create(player_id=player_data["player_id"], defaults=player_data)

        return Response({"message": "Database populated with players"}, status=status.HTTP_201_CREATED)


# class GameInfoView(APIView):
#     def get(self, request, *args, **kwargs):
#         game_id = self.kwargs.get('game_id')

#         try:
#             # Retrieve game and paddle coordinates for the specified game
#             game = Game.objects.get(id=game_id)
#             paddle_coordinates = PaddleCoordinates.objects.filter(game=game)

#             # Serialize the data
#             serializer = GameInfoSerializer({
#                 'game_id': game.id,
#                 'paddle_coordinates': [{'player_id': pc.player_id, 'paddle_y': pc.paddle_y} for pc in paddle_coordinates]
#             })

#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except Game.DoesNotExist:
#             return Response({'error': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class PaddleMoveView(APIView):
#     def post(self, request, *args, **kwargs):
#         game_id = kwargs.get('game_id')  # Access the game_id from URL parameters
#         player_id = request.data.get('player_id')
#         direction = request.data.get('direction')  # 'up' or 'down'

#         try:
#             # Retrieve the specific paddle coordinates
#             paddle_coordinates = get_object_or_404(PaddleCoordinates, game_id=game_id, player_id=player_id)

#             # Increment or decrement paddle_y based on direction
#             if direction == 'up':
#                 paddle_coordinates.paddle_y += 10
#             elif direction == 'down':
#                 paddle_coordinates.paddle_y -= 10

#             paddle_coordinates.save()

#             return Response({'message': 'Paddle coordinates updated successfully'}, status=status.HTTP_200_OK)

#         except PaddleCoordinates.DoesNotExist:
#             return Response({'error': 'Paddle coordinates not found'}, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
