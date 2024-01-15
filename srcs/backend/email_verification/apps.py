from django.apps import AppConfig
from django.core.checks import register, Error, Warning
import os


class EmailVerificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "email_verification"


@register()  # check if env DOMAIN variable is set
def check_host(app_configs, **kwargs):
    errors = []
    if not os.environ.get("DOMAIN"):
        errors.append(
            Error(
                "DOMAIN environment variable is not set",
                hint="Set DOMAIN environment variable to your domain name",
                id="custom_user.E002",
            )
        )
    return errors
