from .models import Stats, MatchHistory
from .serializers import StatsSerializer, MatchHistorySerializer
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from CustomUser.models import CustomUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class MatchHistoryView(APIView):
    serializer_class = MatchHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_match_history(self, user):
        return MatchHistory.objects.filter(Q(user1=user) | Q(user2=user))

    def get(self, request):
        """
        Get user match history based on auth
        """
        match_history = self.get_match_history(request.user)

        serializer = self.serializer_class(match_history, many=True)
        return Response(serializer.data)

    
class MatchHistoryViewById(APIView):
    serializer_class = MatchHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_user(self, user_id):
        return get_object_or_404(CustomUser, id=user_id)

    def get_match_history(self, user):
        return MatchHistory.objects.filter(Q(user1=user) | Q(user2=user))

    def get(self, request, user_id=None):
        """
        Get user match history based on auth or user_id
        """
        user = self.get_user(user_id)
        match_history = self.get_match_history(user)

        serializer = self.serializer_class(match_history, many=True)
        return Response(serializer.data)


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
