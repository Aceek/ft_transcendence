from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import TwoFactorEmailModel


class TwoFactorValidateSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        token = attrs["token"]
        two_factor = TwoFactorEmailModel.objects.get(token=token)
        email = two_factor.user.email
        if two_factor.is_expired():
            raise serializers.ValidationError("2FA code expired.")
        if two_factor.code != attrs["code"]:
            raise serializers.ValidationError("Invalid 2FA code.")
        attrs["email"] = email
        # two_factor.delete()
        return attrs

    def save(self):
        user = get_user_model().objects.get(email=self.validated_data["email"])
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class VerifyEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        try:
            uid_decrypt = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = get_user_model().objects.get(pk=uid_decrypt)
            if (
                not default_token_generator.check_token(user, attrs["token"])
                or not user
            ):
                raise serializers.ValidationError("Invalid verification link.")
        except Exception:
            raise serializers.ValidationError("Invalid verification link.")
        return attrs

    def save(self):
        uid = force_str(urlsafe_base64_decode(self.validated_data["uid"]))
        user = get_user_model().objects.get(pk=uid)
        user.is_active = True
        user.email = user.new_email if user.new_email else user.email
        user.new_email = None
        user.save()
        return user
