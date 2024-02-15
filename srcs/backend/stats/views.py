from .models import Stats, MatchHistory, EloHistory
from .serializers import StatsSerializer, MatchHistorySerializer
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from CustomUser.models import CustomUser
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import F


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 5


class MatchHistoryView(ListAPIView):
    serializer_class = MatchHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        if user_id:
            user = get_object_or_404(CustomUser, id=user_id)
        else:
            user = self.request.user
        queryset = MatchHistory.objects.filter(Q(user1=user) | Q(user2=user)).order_by(
            F("date").desc()
        )
        return queryset


class StatsView(ListAPIView):
    serializer_class = StatsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        user = self.get_user(user_id) if user_id else self.request.user
        stats = self.get_stats(user)
        elo_history = self.get_elo_history(user)
        stats.elo_history = elo_history
        return [stats]

    def get_user(self, user_id):
        return get_object_or_404(CustomUser, id=user_id)

    def get_stats(self, user):
        return get_object_or_404(Stats, user=user)

    def get_elo_history(self, user):
        return EloHistory.objects.filter(user=user).order_by("-created_at")[:10]
