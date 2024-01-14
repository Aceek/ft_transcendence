from rest_framework import serializers
from CustomUser.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["uid", "username", "email", "avatar"]
