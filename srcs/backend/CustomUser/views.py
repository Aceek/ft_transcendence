from rest_framework import viewsets
from .models import CustomUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer
from .serializers import CustomUserSerializerFriend
from rest_framework import exceptions
from rest_framework import mixins


class CustomUserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        if self.action == "remove_friends" or self.action == "update_friends":
            return CustomUserSerializerFriend
        return super().get_serializer_class()

    @action(detail=True, methods=["patch"])
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
