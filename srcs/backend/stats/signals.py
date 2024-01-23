from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Stats
from CustomUser.models import CustomUser

@receiver(post_save, sender=CustomUser)
def create_user_stats(sender, instance, created, **kwargs):
    if created:
        Stats.objects.create(user=instance)