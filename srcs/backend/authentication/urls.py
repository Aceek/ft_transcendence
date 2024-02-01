from rest_framework_simplejwt.views import TokenRefreshView
from django.http import HttpResponse
from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    OAuth42View,
    PingView
)

urlpatterns = [
    path("ping/", PingView.as_view(), name="ping"),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("oauth2/", OAuth42View.as_view(), name="oauth2"),
]
