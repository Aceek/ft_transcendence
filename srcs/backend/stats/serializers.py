from rest_framework import serializers
from .models import Stats, MatchHistory, EloHistory

class EloHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EloHistory
        fields = "__all__"


class StatsSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    elo_history = EloHistorySerializer(many=True, read_only=True)
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
