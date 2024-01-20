from django.urls import path, include
from rest_framework import routers
from .views import CustomUserListView, CustomUserDetailView, CustomUserFriendView

# router = default_router = routers.DefaultRouter()
# router.register(r"users", CustomUserListView, basename="users")


urlpatterns = [
    path("users", CustomUserListView.as_view()),
    path("users/profile", CustomUserDetailView.as_view()),
    path("users/remove_friends", CustomUserFriendView.as_view()),
    # path("", include(router.urls)),
]
