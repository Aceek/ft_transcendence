from .models import Tournament, Matches
from rest_framework import serializers


class MatchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matches
        fields = "__all__"

    def to_representation(self, instance):
        representation = super(MatchesSerializer, self).to_representation(instance)
        request = self.context.get("request")
        if (
            request
            and instance.is_active
            and instance.is_finished == False
            and (instance.user1 == request.user or instance.user2 == request.user)
        ):
            representation["room_url"] = f"/room/tournament/{instance.uid}/"
            representation["ready_to_play"] = True
        return representation


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = "__all__"

    def create(self, validated_data):
        request = self.context["request"]
        if request and hasattr(request, "user"):
            validated_data["ownerUser"] = request.user
        if validated_data["max_participants"] < 2:
            raise serializers.ValidationError("max_participants: should be more than 1")
        if validated_data["max_participants"] > 8:
            raise serializers.ValidationError("max_participants: should be less than 9")
        validated_data["place_left"] = validated_data["max_participants"]
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super(TournamentSerializer, self).to_representation(instance)

        if instance.is_active:
            matches = Matches.objects.filter(tournament=instance)
            representation["matches"] = MatchesSerializer(
                matches, many=True, context=self.context
            ).data
        # if user is in the tournament
        request = self.context.get("request")
        if request and instance.user.filter(id=request.user.id).exists():
            representation["is_joined"] = True
        else:
            representation["is_joined"] = False
        return representation
