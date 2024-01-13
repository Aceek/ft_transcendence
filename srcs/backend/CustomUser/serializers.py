from rest_framework import serializers
from .models import CustomUser
from .validators import validate_username

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["uid", "username", "email", "avatar"]
