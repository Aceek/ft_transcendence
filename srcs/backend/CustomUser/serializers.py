from rest_framework import serializers
from CustomUser.models import CustomUser
import uuid


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "avatar", "is_2fa_enabled", "friends"]

    def update(self, instance, validated_data):
        friends = validated_data.pop("friends", [])
        for friend in friends:
            instance.friends.add(friend)
        return super().update(instance, validated_data)


class CustomUserSerializerFriend(serializers.Serializer):
    friends = serializers.ListField(child=serializers.UUIDField(), required=True)
