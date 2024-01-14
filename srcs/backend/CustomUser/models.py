from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from .storage import OverwriteStorage
from django.urls import reverse
from .validators import (
    validate_username,
    validate_mime_type,
    validate_image_size,
    validate_image_dimensions,
    validate_image_ext,
)

import requests
import uuid
import os


def avatar_image_path(instance, filename):
    ext = filename.split(".")[-1]
    new_filename = f"{instance.username}_pp.{ext}"

    return os.path.join(f"avatars/{instance.uid}", new_filename)


class CustomUser(AbstractUser):
    uid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=20, unique=True, validators=[validate_username]
    )
    is_active = models.BooleanField(default=False)
    avatar = models.ImageField(
        upload_to=avatar_image_path,
        storage=OverwriteStorage(),
        null=True,
        blank=True,
        validators=[
            validate_image_ext,
            validate_mime_type,
            validate_image_size,
            validate_image_dimensions,
        ],
    )


@receiver(pre_delete, sender=CustomUser)
def delete_avatar(sender, instance, **kwargs):
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)
    user_uid_folder = os.path.join(settings.MEDIA_ROOT, "avatars", str(instance.uid))
    if os.path.exists(user_uid_folder):
        if not os.listdir(user_uid_folder):
            os.rmdir(user_uid_folder)


def send_api_verification_email(uid):
    url_relative = reverse("email-verification:email-verification")

    # Construire l'URL complète avec le nom de domaine
    domain = os.environ.get("HOST")  # get the domain name from the environment variable
    complete_url = f"{domain}{url_relative}?uid={uid}"
    try:
        # Envoyer la requête GET à l'URL
        response = requests.get(complete_url)

        # Vérifier si la réponse est réussie (statut HTTP 200)
        if response.status_code == 200:
            print("Requête GET réussie.")
        else:
            print(f"Échec de la requête GET avec le statut : {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'envoi de la requête GET : {str(e)}")


@receiver(pre_save, sender=CustomUser)
def update_is_active_if_email_changed(sender, instance, **kwargs):
    if instance._state.adding:
        return
    try:
        old_instance = CustomUser.objects.get(pk=instance.pk)
        if old_instance.email != instance.email:
            instance.is_active = False
            send_api_verification_email(instance.uid)
    except CustomUser.DoesNotExist:
        pass

