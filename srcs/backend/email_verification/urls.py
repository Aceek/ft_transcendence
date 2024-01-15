from django.urls import path
from .views import TwoFactorVerifyView, VerifyEmailView

urlpatterns = [
    path("validate/", VerifyEmailView.as_view(), name="verify-email"),
    path("2fa/", TwoFactorVerifyView.as_view(), name="2fa"),
]
