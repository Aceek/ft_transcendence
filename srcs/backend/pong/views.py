# pong/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from .game_logic import *
from os import environ
from django.http import JsonResponse

def get_ip_address(request):
    ip_address = environ.get("IP_ADDRESS")
    print('Retrieved IP Address:', ip_address)  # Add print statement
    return JsonResponse({'ip_address': ip_address})


class InitGameView(APIView):
    def post(self, request, *args, **kwargs):
        player1_id = request.data.get('player1_id')
        player2_id = request.data.get('player2_id')

        # Call the initialize_game function to handle game initialization
        result, status_code = initialize_game(player1_id, player2_id)

        # Return the response with the JSON data
        return Response(result, status=status_code)
    
class StartGameView(APIView):
    def post(self, request, *args, **kwargs):
        game_id = request.data.get('game_id')

        if not game_id:
            return Response({'error': 'Game ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the game object from the database
        game = get_object_or_404(Game, id=game_id)

        # Check if the game is not already started
        # if game.is_started:
        #     return Response({'error': 'Game has already started'}, status=status.HTTP_400_BAD_REQUEST)

        # Call the start_game_function with the game object
        start_game(game)

        # Update the game status to indicate that it has started
        # game.is_started = True
        # game.save()

        # # Serialize the game data for response
        # serializer = GameSerializer(game)
        # response_data = serializer.data

        # return Response(response_data, status=status.HTTP_200_OK)

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


class UpdateGameDataView(APIView):
    def get(self, request, game_id, *args, **kwargs):
        try:
            # Retrieve the game, ball coordinates, and related player data in a single query
            game_data = Game.objects.select_related('player1', 'player2', 'ball_coordinates').values(
                'player1__paddle_y',
                'player2__paddle_y',
                'ball_coordinates__x',
                'ball_coordinates__y',
            ).get(id=game_id)

            response_data = {
                'p1_y': game_data['player1__paddle_y'],
                'p2_y': game_data['player2__paddle_y'],
                'b_x': game_data['ball_coordinates__x'],
                'b_y': game_data['ball_coordinates__y'],
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Game.DoesNotExist:
            return Response({'error': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)

class UpdatePaddleView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Deserialize incoming data
            serializer = PaddleUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            player_id = serializer.validated_data['player_id']
            paddle_y = serializer.validated_data['paddle_y']

            # Retrieve player object from the database
            player = Player.objects.get(player_id=player_id)

            # Update the player's paddle_y attribute
            player.paddle_y = paddle_y
            player.save()

            # Serialize updated player data for response
            player_serializer = PlayerSerializer(player)
            serialized_data = player_serializer.data

            return Response({'success': True, 'player': serialized_data}, status=status.HTTP_200_OK)
        except Player.DoesNotExist:
            return Response({'success': False, 'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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