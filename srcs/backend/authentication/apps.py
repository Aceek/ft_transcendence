from django.apps import AppConfig
from django.core.checks import Error, register, Info, Tags
from django.conf import settings
from django.contrib.auth import get_user_model


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"


@register
def check_auth_backends(app_configs, **kwargs):
    if (
        "authentication.backends.EmailModelBackend"
        not in settings.AUTHENTICATION_BACKENDS
    ):
        return [
            Error(
                "EmailModelBackend not found in AUTHENTICATION_BACKENDS",
                hint="Add 'authentication.backends.EmailModelBackend' to AUTHENTICATION_BACKENDS in settings.py",
                id="authentication.E001",
            )
        ]
    return []


@register
def check_oauth2_settings(app_configs, **kwargs):
    if not hasattr(settings, "OAUTH_UID"):
        return [
            Error(
                "OAUTH_UID not found in settings",
                hint="Add OAUTH_UID to settings.py",
                id="authentication.E002",
            )
        ]
    if not hasattr(settings, "OAUTH_REDIRECT_URI"):
        return [
            Error(
                "OAUTH_REDIRECT_URI not found in settings",
                hint="Add OAUTH_REDIRECT_URI to settings.py",
                id="authentication.E003",
            )
        ]
    if not hasattr(settings, "OAUTH_SECRET"):
        return [
            Error(
                "OAUTH_SECRET not found in settings",
                hint="Add OAUTH_SECRET to settings.py",
                id="authentication.E004",
            )
        ]
    return []


@register
def check_upper_validator_settings(app_configs, **kwargs):
    validators = [v["NAME"] for v in settings.AUTH_PASSWORD_VALIDATORS]
    if "authentication.validators.Minimum1UppercaseValidator" not in validators:
        return [
            Info(
                "Minimum1UppercaseValidator not found in AUTH_PASSWORD_VALIDATORS",
                hint="Increase password security by adding 'authentication.validators.Minimum1UppercaseValidator' to AUTH_PASSWORD_VALIDATORS in settings.py",
                id="authentication.I001",
            )
        ]
    return []


@register
def check_lower_validator_settings(app_configs, **kwargs):
    validators = [v["NAME"] for v in settings.AUTH_PASSWORD_VALIDATORS]
    if "authentication.validators.Minimum1LowercaseValidator" not in validators:
        return [
            Info(
                "Minimum1LowercaseValidator not found in AUTH_PASSWORD_VALIDATORS",
                hint="Increase password security by adding 'authentication.validators.Minimum1LowercaseValidator' to AUTH_PASSWORD_VALIDATORS in settings.py",
                id="authentication.I002",
            )
        ]
    return []


@register
def check_number_validator_settings(app_configs, **kwargs):
    validators = [v["NAME"] for v in settings.AUTH_PASSWORD_VALIDATORS]
    if "authentication.validators.Minimum1NumberValidator" not in validators:
        return [
            Info(
                "Minimum1NumberValidator not found in AUTH_PASSWORD_VALIDATORS",
                hint="Increase password security by adding 'authentication.validators.Minimum1NumberValidator' to AUTH_PASSWORD_VALIDATORS in settings.py",
                id="authentication.I003",
            )
        ]
    return []


@register
def check_special_character_validator_settings(app_configs, **kwargs):
    validators = [v["NAME"] for v in settings.AUTH_PASSWORD_VALIDATORS]
    if "authentication.validators.Minimum1SpecialCharacterValidator" not in validators:
        return [
            Info(
                "Minimum1SpecialCharacterValidator not found in AUTH_PASSWORD_VALIDATORS",
                hint="Increase password security by adding 'authentication.validators.Minimum1SpecialCharacterValidator' to AUTH_PASSWORD_VALIDATORS in settings.py",
                id="authentication.I004",
            )
        ]
    return []


@register
def check_smtp_user_settings(app_configs, **kwargs):
    if not hasattr(settings, "EMAIL_HOST_USER") or not settings.EMAIL_HOST_USER:
        return [
            Error(
                "EMAIL_HOST_USER not found in settings",
                hint="Add EMAIL_HOST_USER to settings.py",
                id="authentication.E005",
            )
        ]
    return []


@register
def check_smtp_password_settings(app_configs, **kwargs):
    if not hasattr(settings, "EMAIL_HOST_PASSWORD") or not settings.EMAIL_HOST_PASSWORD:
        return [
            Error(
                "EMAIL_HOST_PASSWORD not found in settings",
                hint="Add EMAIL_HOST_PASSWORD to settings.py",
                id="authentication.E006",
            )
        ]
    return []


@register
def check_2fa_field_user_model(app_configs, **kwargs):
    user_model = get_user_model()
    fields = [field.name for field in user_model._meta.get_fields()]
    if "is_2fa_enabled" in fields:
        return []
    return [
        Error(
            "is_2fa_enabled not found in user model",
            hint="Add is_2fa_enabled as a BooleanField to user model",
            id="authentication.E007",
        )
    ]


@register
def check_jwt_blacklist_installed_app(app_configs, **kwargs):
    if "rest_framework_simplejwt.token_blacklist" not in settings.INSTALLED_APPS:
        return [
            Error(
                "rest_framework_simplejwt.token_blacklist not found in INSTALLED_APPS",
                hint="Add 'rest_framework_simplejwt.token_blacklist' to INSTALLED_APPS in settings.py",
                id="authentication.E008",
            )
        ]
    return []


@register
def check_jwt_installed_app(app_configs, **kwargs):
    if "rest_framework_simplejwt" not in settings.INSTALLED_APPS:
        return [
            Error(
                "rest_framework_simplejwt not found in INSTALLED_APPS",
                hint="Add 'rest_framework_simplejwt' to INSTALLED_APPS in settings.py",
                id="authentication.E009",
            )
        ]
    return []


@register
def check_2fa_field_user_model(app_configs, **kwargs):
    user_model = get_user_model()
    fields = [field.name for field in user_model._meta.get_fields()]
    if "id" in fields:
        return []
    return [
        Error(
            "id not found in user model",
            hint="Add id primary key to user model",
            id="authentication.E010",
        )
    ]
