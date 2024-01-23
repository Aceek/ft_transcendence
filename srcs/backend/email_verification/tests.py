from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from datetime import timedelta
from re import search
from .models import TwoFactorEmailModel

class VerifyEmailTestCase(APITestCase):
    URL = reverse("validate")

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
