from django.apps import AppConfig
from django.conf import settings
from django.core.checks import register, Error, Warning
from django.db import connections
from django.db.utils import OperationalError
from django.contrib.auth import get_user_model
import time
import threading
from django.db import transaction


class CustomuserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "CustomUser"

    def ready(self):
        import CustomUser.signals
        thread = threading.Thread(target=update_users_status_offline)
        thread.start()



def update_users_status_offline():
    time.sleep(5)
    db_conn = connections['default']
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        try:
            db_conn.connect()
        except OperationalError:
            time.sleep(1)
            attempts += 1
        else:
            with transaction.atomic():
                User = get_user_model()
                User.objects.all().update(status='offline', chat_online=False)
            break

@register()
def check_settings(app_configs, **kwargs):
    warnings = []
    if not hasattr(settings, "MEDIA_ROOT") or not settings.MEDIA_ROOT:
        warnings.append(
            Warning(
                "MEDIA_ROOT is not set",
                hint="Add MEDIA_ROOT to your settings.py",
                id="custom_user.W001",
            )
        )

    return warnings


@register()
def check_media_url(app_configs, **kwargs):
    warnings = []
    if hasattr(settings, "MEDIA_URL"):
        # Vérification si MEDIA_URL est vide ou égale à "/"
        if not settings.MEDIA_URL or settings.MEDIA_URL == "/":
            warnings.append(
                Warning(
                    "MEDIA_URL is not set correctly",
                    hint="Set MEDIA_URL in your settings.py to a valid path that is not '/'",
                    id="custom_user.W002",
                )
            )
    return warnings


@register()
def check_auth_user_model(app_configs, **kwargs):
    errors = []
    if getattr(settings, "AUTH_USER_MODEL", "") != "CustomUser.CustomUser":
        errors.append(
            Error(
                "AUTH_USER_MODEL is not set correctly",
                hint='Ensure AUTH_USER_MODEL is set to "CustomUser.CustomUser" in your settings.py',
                id="custom_user.E001",
            )
        )
    return errors
