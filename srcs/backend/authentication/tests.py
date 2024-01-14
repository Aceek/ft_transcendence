from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import mail
from django.utils.timezone import now
from re import search
from datetime import timedelta
from .models import TwoFactorEmailModel


class RegisterTestCase(APITestCase):
    URL = reverse("register")

    def test_register_successful(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
        }
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verification_email = mail.outbox[0].body
        uid_token_match = search(r"uid=(.*)&token=(.*)", verification_email)
        verify_url = reverse("verify-email")
        verify_url += (
            f"?uid={uid_token_match.group(1)}&token={uid_token_match.group(2)}"
        )
        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_existing_email(self):
        user_model = get_user_model()
        user_model.objects.create_user("testuser", "test@example.com", "Password123!")
        data = {
            "username": "testuser2",
            "email": "test@example.com",
            "password": "Password123!",
        }
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"email": ["user with this email already exists."]}
        )

    def test_register_existing_username(self):
        user_model = get_user_model()
        user_model.objects.create_user("testuser", "test@example.com", "Password123!")
        data = {
            "username": "testuser",
            "email": "test1@example.com",
            "password": "Password123!",
        }
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"username": ["A user with that username already exists."]}
        )

    def test_register_not_an_email(self):
        data = {
            "username": "testuser",
            "email": "test@example",
            "password": "Password123!",
        }
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"email": ["Enter a valid email address."]})

    def test_register_password_too_short(self):
        try:
            next(
                validator
                for validator in settings.AUTH_PASSWORD_VALIDATORS
                if validator["NAME"]
                == "django.contrib.auth.password_validation.MinimumLengthValidator"
            )
        except StopIteration:
            return True
        try:
            min_pass_length = next(
                validator
                for validator in settings.AUTH_PASSWORD_VALIDATORS
                if validator["NAME"]
                == "django.contrib.auth.password_validation.MinimumLengthValidator"
            )["OPTIONS"]["min_length"]
        except KeyError:
            return True
        data = {"username": "testuser", "email": "test@example.com", "password": "Pa1!"}
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "password": [
                    f"This password is too short. It must contain at least {min_pass_length} characters."
                ]
            },
        )

    def test_register_password_no_upper(self):
        try:
            next(
                validator
                for validator in settings.AUTH_PASSWORD_VALIDATORS
                if validator["NAME"]
                == "authentication.validators.Minimum1UppercaseValidator"
            )
        except StopIteration:
            return True
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "passsalut1!",
        }
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"password": ["This password must contain at least 1 uppercase letter."]},
        )

    def test_register_password_no_lower(self):
        try:
            next(
                validator
                for validator in settings.AUTH_PASSWORD_VALIDATORS
                if validator["NAME"]
                == "authentication.validators.Minimum1LowercaseValidator"
            )
        except StopIteration:
            return True
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "PASSALUT1!",
        }
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"password": ["This password must contain at least 1 lowercase letter."]},
        )

    def test_register_password_no_number(self):
        try:
            next(
                validator
                for validator in settings.AUTH_PASSWORD_VALIDATORS
                if validator["NAME"]
                == "authentication.validators.Minimum1NumberValidator"
            )
        except StopIteration:
            return True
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "PasSalut!",
        }
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"password": ["This password must contain at least 1 number."]},
        )

    def test_register_password_no_special_character(self):
        try:
            next(
                validator
                for validator in settings.AUTH_PASSWORD_VALIDATORS
                if validator["NAME"]
                == "authentication.validators.Minimum1SpecialCharacterValidator"
            )
        except StopIteration:
            return True
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "PasSalut12",
        }
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"password": ["This password must contain at least 1 special character."]},
        )


class LoginTestCase(APITestCase):
    URL = reverse("login")
    USER_USERNAME = "testuser"
    USER_EMAIL = "testuser@student.42.fr"
    USER_PASSWORD = "PasSalut12!"

    def setUp(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            username=self.USER_USERNAME,
            email=self.USER_EMAIL,
            password=self.USER_PASSWORD,
        )

    def test_login_successful(self):
        data = {"email": self.USER_EMAIL, "password": self.USER_PASSWORD}
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertTrue(response.data["refresh"])
        self.assertTrue(response.data["access"])

    def test_login_wrong_password(self):
        data = {"email": self.USER_EMAIL, "password": "WrongPassword123!"}
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json(),
            {"detail": "No active account found with the given credentials"},
        )

    def test_login_wrong_email(self):
        data = {"email": "wrongemail@student.42.fr", "password": self.USER_PASSWORD}
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json(),
            {"detail": "No active account found with the given credentials"},
        )

    def test_register_login_successful(self):
        register_url = reverse("register")
        data = {
            "username": "testuser2",
            "email": "testuser2@student.42.fr",
            "password": "PasSalut12!",
        }
        self.client.post(register_url, data)
        verification_email = mail.outbox[0].body
        uid_token_match = search(r"uid=(.*)&token=(.*)", verification_email)
        verify_url = reverse("verify-email")
        verify_url += (
            f"?uid={uid_token_match.group(1)}&token={uid_token_match.group(2)}"
        )
        response = self.client.get(verify_url)
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertTrue(response.data["refresh"])
        self.assertTrue(response.data["access"])


class LogoutTestCase(APITestCase):
    URL = reverse("logout")

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.access_token = None
        self.refresh_token = None

    def setUp(self):
        usr_username = "testuser"
        usr_email = "test@example.fr"
        usr_password = "PasSalut12!"
        user_model = get_user_model()
        user_model.objects.create_user(
            username=usr_username,
            email=usr_email,
            password=usr_password,
        )
        login_url = reverse("login")
        data = {"email": usr_email, "password": usr_password}
        response = self.client.post(login_url, data)
        self.access_token = response.data["access"]
        self.refresh_token = response.data["refresh"]

    def test_logout_successful(self):
        header = {"Authorization": f"Bearer {self.access_token}"}
        data = {"refresh": self.refresh_token}
        response = self.client.post(self.URL, data, headers=header)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_no_authenticated(self):
        data = {"refresh": self.refresh_token}
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json(), {"detail": "Authentication credentials were not provided."}
        )

    def test_logout_no_refresh_token(self):
        header = {"Authorization": f"Bearer {self.access_token}"}
        response = self.client.post(self.URL, headers=header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"refresh": ["This field is required."]})

    def test_logout_wrong_refresh_token(self):
        header = {"Authorization": f"Bearer {self.access_token}"}
        data = {"refresh": "wrongrefresh"}
        response = self.client.post(self.URL, data, headers=header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ["Token is invalid or expired"])

    def test_logout_empty_refresh_token(self):
        header = {"Authorization": f"Bearer {self.access_token}"}
        data = {"refresh": ""}
        response = self.client.post(self.URL, data, headers=header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"refresh": ["This field may not be blank."]})


class VerifyEmailTestCase(APITestCase):
    URL = reverse("verify-email")

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.uid = None
        self.token = None
        self.user_username = "testuser"

    def setUp(self):
        user_username = self.user_username
        user_email = "testuser@example.com"
        user_password = "PasSalut12!"
        self.client.post(
            reverse("register"),
            {"username": user_username, "email": user_email, "password": user_password},
        )
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body
        match = search(r"uid=(.*)&token=(.*)", email_body)
        self.assertIsNotNone(match, "UID et Token non trouvés dans l'email")
        self.uid = match.group(1)
        self.token = match.group(2)

    def test_verify_email_successful(self):
        response = self.client.get(self.URL, {"uid": self.uid, "token": self.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {"detail": f"User {self.user_username} has been successfully activated."},
        )

    def test_verify_email_wrong_uid(self):
        response = self.client.get(self.URL, {"uid": "wronguid", "token": self.token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"non_field_errors": ["Invalid verification link."]}
        )

    def test_verify_email_empty_uid(self):
        response = self.client.get(self.URL, {"uid": "", "token": self.token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"uid": ["This field may not be blank."]})

    def test_verify_email_no_uid(self):
        response = self.client.get(self.URL, {"token": self.token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"uid": ["This field is required."]})

    def test_verify_email_wrong_token(self):
        response = self.client.get(self.URL, {"uid": self.uid, "token": "wrongtoken"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"non_field_errors": ["Invalid verification link."]}
        )

    def test_verify_email_empty_token(self):
        response = self.client.get(self.URL, {"uid": self.uid, "token": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"token": ["This field may not be blank."]})

    def test_verify_email_no_token(self):
        response = self.client.get(self.URL, {"uid": self.uid})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"token": ["This field is required."]})

    def test_verify_email_no_data(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"uid": ["This field is required."], "token": ["This field is required."]},
        )


class TwoFactorVerifyTestCase(APITestCase):
    URL = reverse("2fa")

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.twofa = None

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="PasSalut12!",
            is_active=True,
            is_2fa_enabled=True,
        )
        self.twofa = TwoFactorEmailModel.objects.create(user=self.user, code="123456")

    def test_2fa_successful(self):
        response = self.client.post(
            self.URL, {"code": "123456", "token": self.twofa.token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertTrue(response.data["refresh"])
        self.assertTrue(response.data["access"])

    def test_2fa_wrong_code(self):
        response = self.client.post(
            self.URL, {"code": "654321", "token": self.twofa.token}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"non_field_errors": ["Invalid 2FA code."]})

    def test_2fa_expired_code(self):
        self.twofa.expiration = now() - timedelta(minutes=10)
        self.twofa.save()
        response = self.client.post(
            self.URL, {"code": "123456", "token": self.twofa.token}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"non_field_errors": ["2FA code expired."]})

    def test_2fa_no_code(self):
        response = self.client.post(self.URL, {"token": self.twofa.token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"code": ["This field is required."]})

    def test_2fa_empty_code(self):
        response = self.client.post(self.URL, {"code": "", "token": self.twofa.token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"code": ["This field may not be blank."]})

    def test_2fa_no_token(self):
        response = self.client.post(self.URL, {"code": "123456"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"token": ["This field is required."]})

    def test_2fa_empty_token(self):
        response = self.client.post(self.URL, {"code": "123456", "token": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"token": ["Must be a valid UUID."]})
