from rest_framework import serializers
from CustomUser.models import CustomUser
import uuid


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "avatar", "is_2fa_enabled", "friends"]


class CustomUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "avatar", "is_2fa_enabled"]


class CustomUserSerializerFriend(serializers.Serializer):
    friends = serializers.ListField(child=serializers.UUIDField(), required=True)
