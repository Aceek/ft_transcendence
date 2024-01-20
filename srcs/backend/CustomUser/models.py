from django.contrib.auth.models import AbstractUser
from django.db import models
from .storage import OverwriteStorage
from .validators import validate_username, validate_image
import uuid
from .utils import avatar_image_path


class CustomUser(AbstractUser):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=20, unique=True, validators=[validate_username]
    )
    is_active = models.BooleanField(default=False)
    is_2fa_enabled = models.BooleanField(default=False)
    avatar = models.ImageField(
        upload_to=avatar_image_path,
        storage=OverwriteStorage(),
        null=True,
        blank=True,
        validators=[validate_image],
    )
    friends = models.ManyToManyField("self", blank=True, symmetrical=False)
