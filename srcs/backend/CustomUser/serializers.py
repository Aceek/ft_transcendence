from rest_framework import serializers
from CustomUser.models import CustomUser
from email_verification.utils import send_verification_email


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "avatar",
            "is_2fa_enabled",
            "friends",
            "new_email",
        ]
        read_only_fields = ["id", "email"]

    def update(self, instance, validated_data):
        new_email = validated_data.pop("new_email", None)
        if new_email:
            instance.new_email = new_email
            send_verification_email(instance, new_email)
        friends = validated_data.pop("friends", [])
        for friend in friends:
            instance.friends.add(friend)
        return super().update(instance, validated_data)


class CustomUserSerializerFriend(serializers.Serializer):
    friends = serializers.ListField(child=serializers.UUIDField(), required=True)
