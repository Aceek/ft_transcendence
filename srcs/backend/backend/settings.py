"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from os import environ
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ.get("DJANGO_SECRET")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = environ.get("DEBUG_VAR")

ALLOWED_HOSTS = ["api.ft-transcendence.fr", "localhost", ""]

# DRF Spectacular settings
SPECTACULAR_SETTINGS = {
    "SCHEMA_PATH_FUNC": ".",
    "TITLE": "Votre API",
    "DESCRIPTION": "Description de votre API",
}

# DRF settings
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
       'rest_framework.permissions.IsAuthenticated',
    ],
}

# Custom user model
AUTH_USER_MODEL = "CustomUser.CustomUser"

# Chemin où les fichiers médias sont stockés sur le serveur
MEDIA_ROOT = BASE_DIR / "media"

# URL publique pour accéder aux fichiers médias
MEDIA_URL = "/media/"

# Application definition

INSTALLED_APPS = [
    "CustomUser",
    "authentication",
    "email_verification",
    "stats",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_spectacular",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    'corsheaders',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": environ.get("POSTGRES_DB"),
#         "USER": environ.get("POSTGRES_USER"),
#         "PASSWORD": environ.get("POSTGRES_PASSWORD"),
#         "HOST": environ.get("POSTGRES_HOST"),
#         "PORT": environ.get("POSTGRES_PORT"),
#     }
# }

# dev database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "authentication.validators.Minimum1UppercaseValidator",
    },
    {
        "NAME": "authentication.validators.Minimum1LowercaseValidator",
    },
    {
        "NAME": "authentication.validators.Minimum1NumberValidator",
    },
    {
        "NAME": "authentication.validators.Minimum1SpecialCharacterValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "authentication.backends.EmailModelBackend",
]

OAUTH_UID = environ.get("OAUTH_UID")

OAUTH_REDIRECT_URI = environ.get("OAUTH_REDIRECT_URI")

OAUTH_SECRET = environ.get("OAUTH_SECRET")

EMAIL_HOST = environ.get("EMAIL_HOST")

EMAIL_USE_TLS = environ.get("EMAIL_USE_TLS")

EMAIL_PORT = environ.get("EMAIL_PORT")

EMAIL_HOST_USER = environ.get("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = environ.get("EMAIL_HOST_PASSWORD")

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://localhost:443",
]
