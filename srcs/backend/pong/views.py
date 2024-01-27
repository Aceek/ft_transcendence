# pong/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PaddleCoordinates, Game

class InitGameView(APIView):
    def post(self, request, *args, **kwargs):
        player1_id = request.data.get('player1_id')
        player2_id = request.data.get('player2_id')

        try:
            # Create a new game
            game = Game.objects.create(player1_id=player1_id, player2_id=player2_id)

            # Initialize paddle coordinates for player 1 and player 2
            PaddleCoordinates.objects.create(game=game, player_id=player1_id, paddle_y=50)
            PaddleCoordinates.objects.create(game=game, player_id=player2_id, paddle_y=50)

            return Response({'game_id': game.id, 'message': 'Game initialized successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        game_id = request.query_params.get('game_id')

        try:
            # Retrieve paddle coordinates for the specified game
            paddle_coordinates = PaddleCoordinates.objects.filter(game_id=game_id)

            data = {
                'game_id': game_id,
                'paddle_coordinates': [{'player_id': pc.player_id, 'paddle_y': pc.paddle_y} for pc in paddle_coordinates]
            }

            return Response(data, status=status.HTTP_200_OK)

        except Game.DoesNotExist:
            return Response({'error': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaddleMoveView(APIView):
    def post(self, request, *args, **kwargs):
        game_id = request.data.get('game_id')
        player_id = request.data.get('player_id')
        direction = request.data.get('direction')  # 'up' or 'down'

        try:
            # Retrieve the specific paddle coordinates
            paddle_coordinates = PaddleCoordinates.objects.get(game_id=game_id, player_id=player_id)

            # Increment or decrement paddle_y based on direction
            if direction == 'up':
                paddle_coordinates.paddle_y += 1
            elif direction == 'down':
                paddle_coordinates.paddle_y -= 1

            paddle_coordinates.save()

            return Response({'message': 'Paddle coordinates updated successfully'}, status=status.HTTP_200_OK)

        except PaddleCoordinates.DoesNotExist:
            return Response({'error': 'Paddle coordinates not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
