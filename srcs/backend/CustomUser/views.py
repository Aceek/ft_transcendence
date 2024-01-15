from rest_framework import viewsets
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework import exceptions

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    # restrict the user from creating a new user via the API
    # def create(self, request, *args, **kwargs):
    #     raise exceptions.PermissionDenied("You can't create a user via the API")

    def update(self, request, *args, **kwargs):
        if not kwargs.get('partial', False):
            raise exceptions.PermissionDenied("You can't update all user's data via the API")
        return super().update(request, *args, **kwargs)
