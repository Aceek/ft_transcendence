from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from email_verification.utils import send_verification_email
from .models import CustomUser
import os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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
def user_status_activity_on_save(sender, instance, **kwargs):
    if instance._state.adding:
        return
    try:
        old_instance = CustomUser.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            channel_layer = get_channel_layer()
            group_name = f"user_activity_{instance.id}"

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "user_activity",
                    "status": instance.status,
                    "user_id": str(instance.id),
                },
            )
    except CustomUser.DoesNotExist:
        pass



