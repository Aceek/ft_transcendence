from rest_framework import viewsets
from .models import CustomUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer
from .serializers import CustomUserSerializerFriend
from rest_framework import exceptions
from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


# class CustomUserListView(
#     mixins.RetrieveModelMixin,
#     mixins.UpdateModelMixin,
#     mixins.ListModelMixin,
#     viewsets.GenericViewSet,
# ):
#     queryset = CustomUser.objects.all()
#     serializer_class = CustomUserSerializer

#     def get_serializer_class(self):
#         if self.action == "remove_friends" or self.action == "update_friends":
#             return CustomUserSerializerFriend
#         return super().get_serializer_class()


class CustomUserListView(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    # GET /users/ retrieve all users
    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    # PATCH /users/ update friends base on jwt token
    def patch(self, request, format=None):
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

    # GET /users/profile/ retrieve user profile base on jwt token
    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)


class CustomUserFriendView(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializerFriend
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = CustomUserSerializerFriend(data=request.data)

        if serializer.is_valid():
            friends_to_remove = serializer.validated_data["friends"]
            for friend_id in friends_to_remove:
                user.friends.remove(friend_id)
            user.save()
            return_serializer = CustomUserSerializerFriend(user)
            return Response(return_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
