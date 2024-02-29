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

    def validate_email_uniqueness(self, email):
        """_summary_
            verify if the email is not already used by another user

        Args:
            email (_type_): email to verify
        """
        try:
            CustomUser.objects.get(email=email)
            raise serializers.ValidationError("Email already exists")
        except CustomUser.DoesNotExist:
            return

    def validate_oauth_only_email_change(self):
        """_summary_
            verify if the user is an oauth user only
        """
        if not self.instance.has_usable_password():
            raise serializers.ValidationError("Oauth user can't change their email")

    def validate_new_email(self, new_email):
        """_summary_
            validate the new_email field

        Args:
            new_email (_type_): new email to validate

        Returns:
            _type_: new_email if it's valid
        """
        self.validate_email_uniqueness(new_email)
        self.validate_oauth_only_email_change()
        return new_email
        

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
        return super().update(instance, validated_data)


class CustomUserSerializerFriend(serializers.Serializer):
    friends = serializers.ListField(child=serializers.UUIDField(), required=True)
