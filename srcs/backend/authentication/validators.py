from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class Minimum1UppercaseValidator:
    def validate(self, password, user=None):
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("This password must contain at least 1 uppercase letter."),
                code="password_no_upper",
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 uppercase letter.")


class Minimum1LowercaseValidator:
    def validate(self, password, user=None):
        if not any(char.islower() for char in password):
            raise ValidationError(
                _("This password must contain at least 1 lowercase letter."),
                code="password_no_lower",
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 lowercase letter.")


class Minimum1NumberValidator:
    def validate(self, password, user=None):
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("This password must contain at least 1 number."),
                code="password_no_number",
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 number.")


class Minimum1SpecialCharacterValidator:
    def validate(self, password, user=None):
        if not any(not char.isalnum() for char in password):
            raise ValidationError(
                _("This password must contain at least 1 special character."),
                code="password_no_special_character",
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 special character.")
