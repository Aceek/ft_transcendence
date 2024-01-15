from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import mail
from re import search


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
            response.json(), {"username": ["user with this username already exists."]}
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
            is_active=True,
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
        verify_url = reverse("validate")
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
        self.header = None

    def setUp(self):
        usr_username = "testuser"
        usr_email = "test@example.fr"
        usr_password = "PasSalut12!"
        user_model = get_user_model()
        user_model.objects.create_user(
            username=usr_username,
            email=usr_email,
            password=usr_password,
            is_active=True,
        )
        login_url = reverse("login")
        data = {"email": usr_email, "password": usr_password}
        response = self.client.post(login_url, data)
        self.access_token = response.data["access"]
        self.refresh_token = response.data["refresh"]
        self.header = {"Authorization": f"Bearer {self.access_token}"}

    def test_logout_successful(self):
        data = {"refresh": self.refresh_token}
        response = self.client.post(self.URL, data, headers=self.header)
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