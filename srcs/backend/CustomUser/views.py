from .models import CustomUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer, CustomUserSerializerFriend
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .services import remove_friend
from django.shortcuts import get_object_or_404


class CustomUserListView(APIView):
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserDetailView(APIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_user(self, user_id):
        return get_object_or_404(CustomUser, id=user_id)

    def get(self, request, user_id=None):
        """
        Get user profile based on auth or user_id
        """
        user = self.get_user(user_id) if user_id else request.user

        serializer = self.serializer_class(user)
        return Response(serializer.data)


class CustomUserFriendView(APIView):
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
