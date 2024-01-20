from .models import CustomUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer, CustomUserSerializerFriend
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .services import remove_friend
from rest_framework import exceptions
import uuid


class CustomUserListView(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    # GET /users/ retrieve all users
    def get(self, request, format=None):
        """
        Get all users
        """
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    def patch(self, request, format=None):
        """
        Update user profile base on auth token
        """
        user = request.user
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class CustomUserDetailView(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        """
        Get user profile base on auth or user_id
        """
        if user_id:
            try:
                uuid.UUID(user_id, version=4)
            except ValueError:
                raise exceptions.ValidationError(detail="Invalid user_id")

            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                raise exceptions.NotFound(detail="User does not exist")
        else:
            user = request.user

        serializer = CustomUserSerializer(user)
        return Response(serializer.data)


class CustomUserFriendView(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializerFriend
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        """
        Remove friends from user
        """
        user = request.user
        serializer = CustomUserSerializerFriend(data=request.data)

        if serializer.is_valid():
            remove_friend(user, serializer.validated_data["friends"])
            return_serializer = CustomUserSerializerFriend(
                user.friends.all(), many=True
            )
            return Response(return_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
