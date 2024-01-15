from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import serializers
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
import os


# class SendVerificationEmailSerializer(serializers.Serializer):
#     def __init__(self, user, *args, **kwargs):
#         self.user = user
#         super().__init__(*args, **kwargs)

#     def send_verification_email(self):
#         user = self.user  # Utilisez l'utilisateur passé au sérialiseur

#         # Le reste du code pour envoyer l'e-mail de vérification reste inchangé
#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         token = default_token_generator.make_token(user)

#         # Construisez le lien de vérification en fonction de votre configuration
#         current_site = get_current_site(self.context["request"])
#         verification_link = f"https://{current_site.domain}/verify_email/{uid}/{token}/"
#         print(verification_link)

#         # Envoyez l'e-mail de vérification
#         subject = "Vérification d'e-mail"
#         message = f"Cliquez sur ce lien pour vérifier votre adresse e-mail : {verification_link}"
#         from_email = "noreply@example.com"
#         recipient_list = [user.email]

#         send_mail(subject, message, from_email, recipient_list, fail_silently=False)


# class VerifyEmailSerializer(serializers.Serializer):
#     uid = serializers.CharField()

#     def validate(self, attrs):
#         try:
#             uid = attrs["uid"]
#             user = get_user_model().objects.get(pk=uid)
#             if not user:
#                 raise serializers.ValidationError("Invalid user.")
#             if user.is_active:
#                 raise serializers.ValidationError("Account already activated.")
#         except Exception:
#             raise serializers.ValidationError("Invalid verification link.")
#         return attrs

#     def send_mail(self):
#         user = get_user_model().objects.get(pk=self.validated_data["uid"])
#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         token = default_token_generator.make_token(user)
#         domain = os.environ.get("HOST")
#         url_api = reverse(
#             "email-verification:email-verification"
#         )  # a changer par la bonne view (url_api)
#         verification_link = f"{domain}{url_api}?uid={uid}&token{token}/"

#         subject = "Vérification d'e-mail"
#         message = f"Cliquez sur ce lien pour vérifier votre adresse e-mail : {verification_link}"
#         recipient_list = [user.email]

#         send_mail(subject, message, None, recipient_list, fail_silently=False)
