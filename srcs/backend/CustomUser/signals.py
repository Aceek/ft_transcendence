from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from email_verification.utils import send_verification_email
import os

from .models import CustomUser


@receiver(pre_delete, sender=CustomUser)
def delete_avatar(sender, instance, **kwargs):
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)
    user_uid_folder = os.path.join(settings.MEDIA_ROOT, "avatars", str(instance.id))
    if os.path.exists(user_uid_folder):
        if not os.listdir(user_uid_folder):
            os.rmdir(user_uid_folder)


@receiver(pre_save, sender=CustomUser)
def update_is_active_if_email_changed(sender, instance, **kwargs):
    if instance._state.adding:
        return
    try:
        old_instance = CustomUser.objects.get(pk=instance.pk)
        if old_instance.email != instance.email:
            instance.is_active = False
            send_verification_email(instance)
    except CustomUser.DoesNotExist:
        pass
