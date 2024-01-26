# pong/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PaddleCoordinates

class PaddleMoveView(APIView):
    def post(self, request, *args, **kwargs):
        game_id = request.data.get('game_id')
        paddle_left_y = request.data.get('paddle_left_y')
        paddle_right_y = request.data.get('paddle_right_y')

        try:
            paddle_coordinates = PaddleCoordinates.objects.get(game_id=game_id)
            paddle_coordinates.paddle_left_y = paddle_left_y
            paddle_coordinates.paddle_right_y = paddle_right_y
            paddle_coordinates.save()

            return Response({'message': 'Paddle coordinates updated successfully'}, status=status.HTTP_200_OK)

        except PaddleCoordinates.DoesNotExist:
            return Response({'error': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
