from .models import Stats, MatchHistory
from .serializers import StatsSerializer, MatchHistorySerializer
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from CustomUser.models import CustomUser
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination


class MatchHistoryView(ListAPIView):
    serializer_class = MatchHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        if user_id:
            user = get_object_or_404(CustomUser, id=user_id)
        else:
            user = self.request.user
        return MatchHistory.objects.filter(Q(user1=user) | Q(user2=user))


class StatsView(ListAPIView):
    serializer_class = StatsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        user = self.get_user(user_id) if user_id else self.request.user
        return Stats.objects.filter(user=user)

    def get_user(self, user_id):
        return get_object_or_404(CustomUser, id=user_id)
