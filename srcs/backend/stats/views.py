from .models import Stats, MatchHistory
from .serializers import StatsSerializer, MatchHistorySerializer
from rest_framework import viewsets
from rest_framework import mixins
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from CustomUser.models import CustomUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class MatchHistoryView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = MatchHistorySerializer
    queryset = MatchHistory.objects.none()

    def get_queryset(self):
        user = self.request.user
        return MatchHistory.objects.filter(Q(user1=user) | Q(user2=user))


class StatsView(APIView):
    serializer_class = StatsSerializer
    permission_classes = [IsAuthenticated]

    def get_user(self, user_id):
        return get_object_or_404(CustomUser, id=user_id)

    def get_stats(self, user):
        return get_object_or_404(Stats, user=user)

    def get(self, request, user_id=None):
        """
        Get user stats based on auth or user_id
        """
        user = self.get_user(user_id) if user_id else request.user
        stats = self.get_stats(user)

        serializer = self.serializer_class(stats)
        return Response(serializer.data)
