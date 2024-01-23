from django.urls import path
from .views import (
    CustomUserListView,
    CustomUserDetailView,
    CustomUserFriendView,
    CustomUserUpdateView,
)


urlpatterns = [
    path("users", CustomUserListView.as_view(), name="users"),
    path("users/profile/me", CustomUserDetailView.as_view(), name="profile"),
    path(
        "users/profile/<uuid:user_id>",
        CustomUserDetailView.as_view(),
        name="profile_by_user_id",
    ),
    path("users/profile/update", CustomUserUpdateView.as_view(), name="update_profile"),
    path("users/remove_friends", CustomUserFriendView.as_view(), name="remove_friends"),
]
