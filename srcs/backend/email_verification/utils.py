from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from os import environ
from .models import TwoFactorEmailModel


def send_verification_email(user):
    if not user or not user.email or user.is_active:
        return
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    domain = environ.get("DOMAIN")
    url_api = reverse("validate")
    verification_link = f"{domain}{url_api}?uid={uid}&token={token}/"

    subject = "Vérification d'e-mail"
    message = (
        f"Cliquez sur ce lien pour vérifier votre adresse e-mail : {verification_link}"
    )
    recipient_list = [user.email]

    send_mail(subject, message, None, recipient_list, fail_silently=False)


def initiate_2fa(user):
    instance_2fa = TwoFactorEmailModel.objects.create(user=user)
    instance_2fa.send_two_factor_email()
    return instance_2fa
