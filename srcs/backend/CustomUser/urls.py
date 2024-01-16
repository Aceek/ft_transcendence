from django.urls import path, include
from rest_framework import routers
from .views import CustomUserViewSet

router = default_router = routers.DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="users")


urlpatterns = [
    path("", include(router.urls)),
]
