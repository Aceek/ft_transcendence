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
            "blocked_users",
        ]
        read_only_fields = ["id", "email"]

    def update(self, instance, validated_data):
        """_summary_
            override the update method to handle the new_email and friends fields

        Args:
            instance (_type_): CustomUser instance
            validated_data (_type_): after validation, the data to update

        Returns:
            _type_: call the super update method who will update the instance
        """
        new_email = validated_data.pop("new_email", None)
        if new_email:
            instance.new_email = new_email
            send_verification_email(instance, new_email)
        friends = validated_data.pop("friends", [])
        for friend in friends:
            instance.friends.add(friend)
        blocked_users = validated_data.pop("blocked_users", [])
        for blocked_user in blocked_users:
            instance.blocked_users.add(blocked_user)
        return super().update(instance, validated_data)


class CustomUserSerializerFriend(serializers.Serializer):
    friends = serializers.ListField(child=serializers.UUIDField(), required=True)

class CustomUserSerializerBlocked(serializers.Serializer):
    blocked_users = serializers.ListField(child=serializers.UUIDField(), required=True)
