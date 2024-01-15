from rest_framework import viewsets
from .models import CustomUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer
from .serializers import CustomUserSerializerFriend
from django.core.exceptions import ObjectDoesNotExist
from .serializers import CustomUserUpdateSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        if self.action == "remove_friends":
            return CustomUserSerializerFriend
        elif self.request.method == 'PATCH':
            return CustomUserUpdateSerializer
        return super().get_serializer_class()

    # restrict the user from creating a new user via the API
    # def create(self, request, *args, **kwargs):
    #     raise exceptions.PermissionDenied("You can't create a user via the API")

    @action(
        detail=True,
        methods=["patch"],
        serializer_class=CustomUserSerializerFriend,
    )
    def remove_friends(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            friends_to_remove = serializer.validated_data["friends"]
            for friend_id in friends_to_remove:
                user.friends.remove(friend_id)
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["patch"],
        serializer_class=CustomUserSerializerFriend,
    )
    def update_friends(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            new_friends = serializer.validated_data.get("friends", [])
            current_friends = user.friends.all()

            for friend_id in new_friends:
                try:
                    friend = CustomUser.objects.get(id=friend_id)
                    if friend_id != user.id and friend_id not in current_friends:
                        user.friends.add(friend)
                except ObjectDoesNotExist:
                    return Response(
                        {"error": f"User with id {friend_id} does not exist."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            user.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
