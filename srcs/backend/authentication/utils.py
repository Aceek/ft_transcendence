from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from .models import TwoFactorEmailModel
from random import randint, choice


def send_verification_email(user):
    subject = "ft-transcendence.fr | Verify your email"
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    domain = reverse("verify-email")
    verification_link = f"{domain}?uid={uid}&token={token}"
    message = (
        f"Hi {user.username},\n\n"
        f"Please click on the following link to verify your email address: {verification_link}\n\n"
        "Thanks."
    )
    send_mail(
        subject=subject, message=message, from_email=None, recipient_list=[user.email]
    )


def generate_random_username():
    min_length = 4
    max_length = 20
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789_-."

    length = randint(min_length, max_length)
    return "".join(choice(allowed_chars) for _ in range(length))


def initiate_2fa(user):
    instance_2fa = TwoFactorEmailModel.objects.create(user=user)
    instance_2fa.send_two_factor_email()
    return instance_2fa
