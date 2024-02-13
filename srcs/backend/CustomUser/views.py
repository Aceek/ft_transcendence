from .models import CustomUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer, CustomUserSerializerFriend
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .services import remove_friend
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination


class CustomUserListView(ListAPIView):
    """
    List all users
    """

    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned users to a given user,
        by filtering against a `search` query parameter in the URL.
        """
        queryset = CustomUser.objects.all()
        search_query = self.request.query_params.get("search", None)

        if search_query is not None:
            queryset = queryset.filter(username__icontains=search_query)

        return queryset


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


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 5


class ListUserFriendsView(ListAPIView):
    """
    List all friends base on authenticated user or user_id
    """

    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        if self.kwargs.get("user_id"):
            return list(
                get_object_or_404(
                    CustomUser, id=self.kwargs.get("user_id")
                ).friends.all()
            )
        return list(self.request.user.friends.all())

    def paginate_queryset(self, queryset):
        if (
            self.paginator
            and self.request.query_params.get(self.paginator.page_query_param, None)
            is None
        ):
            return None
        return super().paginate_queryset(queryset)
