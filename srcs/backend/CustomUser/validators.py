from django.core.exceptions import ValidationError
import mimetypes

from PIL import Image

import re

MAX_WIDTH = 450
MAX_HEIGHT = 450
MIN_WIDTH = 100
MIN_HEIGHT = 100


def validate_username(username):
    if len(username) < 4 or len(username) > 20:
        raise ValidationError(
            "Le nom d'utilisateur doit contenir entre 4 et 20 caractères."
        )

    if not re.match("^[a-zA-Z0-9_.-]*$", username):
        raise ValidationError(
            "Le nom d'utilisateur ne doit contenir que des lettres, des chiffres, des points, des tirets et des tirets bas."
        )


def validate_image(value):
    validate_image_size(value)
    validate_mime_type(value)
    validate_image_dimensions(value)
    validate_image_ext(value)


def validate_image_size(value):
    max_size = 3 * 1024 * 1024  # 3 MB
    if value.size > max_size:
        raise ValidationError("La taille du fichier ne doit pas dépasser 3 Mo.")


def validate_mime_type(value, allowed_mime_types=["image/jpeg", "image/png"]):
    mime_type, _ = mimetypes.guess_type(value.name)
    if mime_type not in allowed_mime_types:
        raise ValidationError(
            "Le type MIME de l'image n'est pas pris en charge. (jpeg, png))"
        )


def validate_image_dimensions(value):
    image = Image.open(value)
    width, height = image.size

    if width < MIN_WIDTH or height < MIN_HEIGHT:
        raise ValidationError(
            "Les dimensions de l'image doivent être au moins de 100x100 pixels."
        )
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        raise ValidationError(
            "Les dimensions de l'image ne doivent pas dépasser 450x450 pixels."
        )


def validate_image_ext(value, allowed_formats=["jpeg", "png"]):
    image_extension = value.name.split(".")[-1].lower()

    if image_extension not in allowed_formats:
        raise ValidationError("L'extension du fichier n'est pas autorisée. (jpeg, png)")
