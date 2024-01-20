from django.urls import path, re_path
from rest_framework import routers
from .views import CustomUserListView, CustomUserDetailView, CustomUserFriendView

# router = default_router = routers.DefaultRouter()
# router.register(r"users", CustomUserListView, basename="users")


urlpatterns = [
    path("users", CustomUserListView.as_view()),
    path("users/profile", CustomUserDetailView.as_view()),
    re_path(r'^users/profile/(?P<user_id>[0-9a-f-]+)$', CustomUserDetailView.as_view()),
    path("users/remove_friends", CustomUserFriendView.as_view()),
    # path("", include(router.urls)),
]
