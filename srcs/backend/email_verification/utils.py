from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from os import environ
from .models import TwoFactorEmailModel
from CustomUser.models import CustomUser


def send_verification_email(user: CustomUser, new_email: str = None):
    """_summary_
        Field new_email is optional. If it is not provided, the user's email will be used.
        Send an email to the user with a link to verify their email address.

    Args:
        user (CustomUser): _description_
        new_email (str, optional): U can precise new_email to change default mail. Defaults to None.
    """
    if not user or not user.email:
        return
    mail = new_email if new_email else user.email
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    domain = environ.get("DOMAIN")
    verification_link = f"{domain}?uid={uid}&token={token}"

    subject = "Vérification d'e-mail"
    message = (
        f"Cliquez sur ce lien pour vérifier votre adresse e-mail : {verification_link}"
    )
    recipient_list = [mail]

    send_mail(subject, message, None, recipient_list, fail_silently=False)


def initiate_2fa(user: CustomUser):
    """_summary_
        Create and send a 2FA token to the user's email.
    Args:
        user (CustomUser): user to send 2FA token to

    Returns:
        TwoFactorEmailModel: instance of TwoFactorEmailModel
    """
    instance_2fa = TwoFactorEmailModel.objects.create(user=user)
    instance_2fa.send_two_factor_email()
    return instance_2fa
