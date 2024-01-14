from django.urls import path
from .views import SendVerificationEmailView

app_name = "email-verification"

urlpatterns = [
    path(
        "email-verification/",
        SendVerificationEmailView.as_view(),
        name="email-verification",
    ),
    # Ajoutez d'autres URL pour les vues de vérification et de confirmation de l'e-mail si nécessaire
]
