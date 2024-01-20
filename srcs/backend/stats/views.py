from .models import Stats, MatchHistory
from .serializers import StatsSerializer, MatchHistorySerializer
from rest_framework import viewsets
from rest_framework import mixins
from django.db.models import Q

# Create your views here.


class StatsView(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Stats.objects.all()
    serializer_class = StatsSerializer


class MatchHistoryView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = MatchHistorySerializer
    queryset = MatchHistory.objects.none()

    def get_queryset(self):
        user = self.request.user
        return MatchHistory.objects.filter(Q(user1=user) | Q(user2=user))
