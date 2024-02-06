from .models import CustomUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer, CustomUserSerializerFriend
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .services import remove_friend
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView


class CustomUserListView(ListAPIView):
    """
    List all users
    """

    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.all()


class CustomUserUpdateView(UpdateAPIView):
    """
    Update user base on authenticated user
    """

    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CustomUserDetailView(RetrieveAPIView):
    """
    Get user base on authenticated user
    """

    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get("user_id")
        return (
            get_object_or_404(CustomUser, id=user_id) if user_id else self.request.user
        )


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
        
class ListUserFriendsView(ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return list(self.request.user.friends.all())





# class RetrieveUserFriendsView(RetrieveAPIView):
#     serializer_class = CustomUserSerializer
#     permission_classes = [IsAuthenticated]

#     def retrieve(self, request, *args, **kwargs):
#         user = self.request.user
#         friend_ids = user.friends.all()  # Liste d'ID d'amis

#         friends_data = []
#         for friend_id in friend_ids:
#             try:
#                 friend = CustomUser.objects.get(id=friend_id)
#                 serializer = self.serializer_class(friend)
#                 friends_data.append(serializer.data)
#             except CustomUser.DoesNotExist:
#                 # Gérer le cas où l'ami n'existe pas
#                 pass

#         return Response(friends_data, status=status.HTTP_200_OK)


