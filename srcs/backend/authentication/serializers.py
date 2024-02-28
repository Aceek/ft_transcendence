from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.utils.crypto import get_random_string
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from oauthlib.oauth2 import InvalidGrantError
from requests_oauthlib import OAuth2Session
from random import randint
from email_verification.utils import initiate_2fa, send_verification_email


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "password", "email")

    def validate_email(self, value):
        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate_username(self, value):
        if get_user_model().objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            is_active=False,
        )
        send_verification_email(user)
        return user


class EmailTokenObtainSerializer(TokenObtainSerializer):
    username_field = get_user_model().EMAIL_FIELD


class LoginSerializer(EmailTokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.is_2fa_enabled:
            instance_2fa = initiate_2fa(self.user)
            return {
                "detail": "2FA code sent to your email.",
                "2FA": f"{instance_2fa.token}",
            }
        refresh = self.get_token(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data


class User42Serializer(serializers.Serializer):
    login = serializers.CharField()
    email = serializers.EmailField()

    def create(self, validated_data):
        user, created = get_user_model().objects.get_or_create(
            email=validated_data["email"]
        )
        if created:
            user.set_unusable_password()
            user.username = self.generate_username(validated_data["login"])
            user.is_active = True
            user.save()
        return user

    def generate_username(self, login):
        username = login
        while get_user_model().objects.filter(username=username).exists():
            username = get_random_string(
                length=randint(6, 20),
                allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789_-.",
            )
        return username


class OAuth42Serializer(serializers.Serializer):
    API_URL = "https://api.intra.42.fr/"
    code = serializers.CharField(required=False, allow_blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oauth = OAuth2Session(
            settings.OAUTH_UID, redirect_uri=settings.OAUTH_REDIRECT_URI
        )

    def validate(self, attrs):
        code = attrs.get("code")
        if code:
            return self.handle_code_validation(code)
        else:
            return self.get_authorization_url()

    def handle_code_validation(self, code):
        token = self.exchange_code(code)
        user_data = self.query_42_api(token)
        return self.handle_user_data_validation(user_data)

    def handle_user_data_validation(self, user_data):
        serializer = User42Serializer(data=user_data)
        if serializer.is_valid():
            return self.handle_user_creation(serializer)
        else:
            raise serializers.ValidationError(serializer.errors)

    def handle_user_creation(self, serializer):
        user = serializer.save()
        if user.is_2fa_enabled:
            return self.handle_2fa(user)
        return self.generate_token_data(user)

    def handle_2fa(self, user):
        instance_2fa = initiate_2fa(user)
        return {
            "detail": "2FA code sent to your email.",
            "2FA": f"{instance_2fa.token}",
        }

    def generate_token_data(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def get_authorization_url(self):
        authorization_url, state = self.oauth.authorization_url(
            self.API_URL + "oauth/authorize"
        )
        return {"authorization_url": authorization_url}

    def exchange_code(self, code):
        try:
            token = self.oauth.fetch_token(
                self.API_URL + "oauth/token",
                client_secret=settings.OAUTH_SECRET,
                code=code,
            )
            return token.get("access_token")
        except InvalidGrantError:
            raise serializers.ValidationError("Invalid authorization code.")

    def query_42_api(self, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self.oauth.get(self.API_URL + "v2/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        raise serializers.ValidationError("Invalid access token.")
