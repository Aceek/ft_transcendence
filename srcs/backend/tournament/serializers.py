from .models import Tournament, Matches, LocalTournament, LocalMatches
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

        matches = Matches.objects.filter(tournament=instance)
        if matches:
            representation["matches"] = MatchesSerializer(
                matches, many=True, context=self.context
            ).data
        # if user is in the tournament
        request = self.context.get("request")
        if request and instance.user.filter(id=request.user.id).exists():
            representation["is_joined"] = True
        else:
            representation["is_joined"] = False

        # if user is the owner of the tournament
        if request and instance.ownerUser == request.user:
            representation["is_owner"] = True
        else:
            representation["is_owner"] = False
        return representation


class LocalMatchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalMatches
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super(LocalMatchesSerializer, self).to_representation(instance)
        request = self.context.get("request")
        if (
            request
            and instance.is_active
            and instance.is_finished == False
            and (instance.room_url and instance.room_url != "")
        ):
            representation["ready_to_play"] = True
        representation["local"] = True
        return representation


class LocalTournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalTournament
        fields = "__all__"

    def create(self, validated_data):
        request = self.context["request"]
        if request and hasattr(request, "user"):
            validated_data["localOwnerUser"] = request.user

        participants = validated_data.get("participants", [])
        if not participants:
            raise serializers.ValidationError(
                {"participants": "La liste des participants ne peut pas être vide."}
            )
        tournament = LocalTournament.objects.create(**validated_data)
        return tournament
    
    def to_representation(self, instance):
        representation = super(LocalTournamentSerializer, self).to_representation(instance)

        matches = LocalMatches.objects.filter(tournament=instance)
        if matches:
            representation["matches"] = LocalMatchesSerializer(
                matches, many=True, context=self.context
            ).data

        return representation

