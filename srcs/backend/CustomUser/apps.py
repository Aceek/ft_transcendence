from django.apps import AppConfig
from django.conf import settings
from django.core.checks import register, Error, Warning


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
    print(settings.MEDIA_URL)
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


class CustomuserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "CustomUser"
