from rest_framework import serializers
from .models import Stats, MatchHistory


class StatsSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = Stats
        fields = "__all__"


class MatchHistorySerializer(serializers.ModelSerializer):
    user1 = serializers.StringRelatedField()
    user2 = serializers.StringRelatedField()
    winner = serializers.StringRelatedField()

    class Meta:
        model = MatchHistory
        fields = "__all__"
