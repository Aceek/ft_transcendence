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

    return os.path.join(f"avatars/{instance.id}", new_filename)


class CustomUser(AbstractUser):
    id = models.UUIDField(
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
    is_2fa_enabled = models.BooleanField(default=False)


@receiver(pre_delete, sender=CustomUser)
def delete_avatar(sender, instance, **kwargs):
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)
    user_uid_folder = os.path.join(settings.MEDIA_ROOT, "avatars", str(instance.id))
    if os.path.exists(user_uid_folder):
        if not os.listdir(user_uid_folder):
            os.rmdir(user_uid_folder)


def send_api_verification_email(uid):
    print("j'envoi l'email frero\n")


@receiver(pre_save, sender=CustomUser)
def update_is_active_if_email_changed(sender, instance, **kwargs):
    if instance._state.adding:
        return
    try:
        old_instance = CustomUser.objects.get(pk=instance.pk)
        if old_instance.email != instance.email:
            instance.is_active = False
            send_api_verification_email(instance.id)
    except CustomUser.DoesNotExist:
        pass

