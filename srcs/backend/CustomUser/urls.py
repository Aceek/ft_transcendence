from django.urls import path
from .views import CustomUserListView, CustomUserDetailView, CustomUserFriendView


urlpatterns = [
    path("users", CustomUserListView.as_view()),
    path("users/profile/me", CustomUserDetailView.as_view(), name="profile"),
    path(
        "users/profile/<uuid:user_id>",
        CustomUserDetailView.as_view(),
        name="profile_by_user_id",
    ),
    path("users/remove_friends", CustomUserFriendView.as_view()),
]
