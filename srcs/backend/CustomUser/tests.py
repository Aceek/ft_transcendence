from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from .models import CustomUser
from rest_framework.test import APIClient
from django.test import override_settings
import shutil
import io
import uuid
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

TEST_DIR = "tests"


@override_settings(MEDIA_ROOT=(TEST_DIR + "/media"))
class CustomUserAPITest(TestCase):
    VALID_IMAGE_SIZE = (100, 100)
    LARGE_IMAGE_SIZE = (3000, 3000)

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.fr",
            password="PasSalut12!",
            is_active=True,
            avatar=self.create_test_image("valid_avatar.png"),
        )
        self.user.save()
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def create_test_image(
        self, image_name, size=VALID_IMAGE_SIZE, image_mode="RGB", image_format="PNG"
    ):
        file = io.BytesIO()
        image = Image.new(image_mode, size)
        image.save(file, format=image_format)
        file.name = image_name
        file.seek(0)
        return SimpleUploadedFile(
            name=file.name, content=file.getvalue(), content_type="image/png"
        )

    def test_update_user_with_large_avatar(self):
        url = reverse("update_profile")
        large_avatar = self.create_test_image(
            "large_avatar.png", size=self.LARGE_IMAGE_SIZE
        )
        response = self.client.patch(url, {"avatar": large_avatar}, format="multipart")
        self.assertNotEqual(response.status_code, 200)

    def test_update_user_with_valid_avatar(self):
        url = reverse("update_profile")
        valid_avatar = self.create_test_image("valid_avatar.png")
        response = self.client.patch(url, {"avatar": valid_avatar}, format="multipart")
        self.assertEqual(response.status_code, 200)

    def test_update_user_with_bad_format_ext_avatar(self):
        url = reverse("update_profile")
        bad_format_avatar = self.create_test_image("bad_format_avatar.bmp")
        response = self.client.patch(
            url, {"avatar": bad_format_avatar}, format="multipart"
        )
        self.assertNotEqual(response.status_code, 200)

    def test_update_user_with_bad_mime_type_avatar(self):
        url = reverse("update_profile")
        bad_mime_type_avatar = self.create_test_image(
            "bad_mime_type_avatar.png", image_format="PDF"
        )
        response = self.client.patch(
            url, {"avatar": bad_mime_type_avatar}, format="multipart"
        )
        self.assertNotEqual(response.status_code, 200)

    def test_update_user_bad_username_to_short(self):
        url = reverse("update_profile")
        response = self.client.patch(url, {"username": "a"}, format="multipart")
        self.assertNotEqual(response.status_code, 200)

    def test_update_user_bad_username_to_long(self):
        url = reverse("update_profile")
        response = self.client.patch(url, {"username": "a" * 21}, format="multipart")
        self.assertNotEqual(response.status_code, 200)

    def test_update_user_bad_username_with_special_chars(self):
        url = reverse("update_profile")
        response = self.client.patch(url, {"username": "a!b"}, format="multipart")
        self.assertNotEqual(response.status_code, 200)

    def test_update_user_bad_username_with_spaces(self):
        url = reverse("update_profile")
        response = self.client.patch(url, {"username": "a b"}, format="multipart")
        self.assertNotEqual(response.status_code, 200)

    def test_update_user_bad_username_with_emoji(self):
        url = reverse("update_profile")
        response = self.client.patch(url, {"username": "😀"}, format="multipart")
        self.assertNotEqual(response.status_code, 200)

    def test_update_user_not_unique_username(self):
        user = CustomUser.objects.create_user(username="testuser2")
        url = reverse("update_profile")
        response = self.client.patch(
            url, {"username": user.username}, format="multipart"
        )
        self.assertNotEqual(response.status_code, 200)

    def test_update_user_not_unique_email(self):
        user = CustomUser.objects.create_user(
            username="testuser2", email="test@user2.42"
        )
        url = reverse("update_profile")
        response = self.client.patch(url, {"email": user.email}, format="multipart")
        self.assertNotEqual(response.status_code, 200)

    def tearDown(self):
        try:
            shutil.rmtree(TEST_DIR, ignore_errors=True)
        except OSError:
            pass


class CustomUserFriendshipTest(TestCase):
    def setUp(self):
        self.client1, self.user1 = self.create_authenticated_client(
            "user1",
            "user1@mail.fr",
        )
        self.client2, self.user2 = self.create_authenticated_client(
            "user2", "user2@mail.fr"
        )
        self.client3, self.user3 = self.create_authenticated_client(
            "user3", "user3@mail.fr"
        )

    def create_authenticated_client(self, username, email):
        client = APIClient()
        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password="PasSalut12!",
            is_active=True,
        )
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
        return client, user

    def test_add_friend(self):
        response = self.client1.patch(
            reverse("update_profile"),
            {"friends": [str(self.user2.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.assertTrue(self.user2 in self.user1.friends.all())

    def test_add_multiple_friend(self):
        response = self.client1.patch(
            reverse("update_profile"),
            {"friends": [str(self.user2.id), str(self.user3.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.assertTrue(self.user2 in self.user1.friends.all())
        self.assertTrue(self.user3 in self.user1.friends.all())

    def test_add_multiple_friend_mutliple_request(self):
        response = self.client1.patch(
            reverse("update_profile"),
            {"friends": [str(self.user2.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        response = self.client1.patch(
            reverse("update_profile"),
            {"friends": [str(self.user3.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.assertTrue(self.user2 in self.user1.friends.all())
        self.assertTrue(self.user3 in self.user1.friends.all())

    def test_add_friend_already_friend(self):
        self.user1.friends.add(self.user2)
        response = self.client1.patch(
            reverse("update_profile"),
            {"friends": [str(self.user2.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        friends = self.user1.friends.all()
        count = sum(1 for friend in friends if friend == self.user2)
        self.assertEqual(count, 1)

    def test_add_friend_not_found(self):
        response = self.client1.patch(
            reverse("update_profile"),
            {"friends": [str(uuid.uuid4())]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_add_friend_bad_request(self):
        response = self.client1.patch(
            reverse("update_profile"),
            {"friends": "bad"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_remove_friend(self):
        self.user1.friends.add(self.user2)
        response = self.client1.patch(
            reverse("remove_friends"),
            {"friends": [str(self.user2.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.assertFalse(self.user2 in self.user1.friends.all())

    def test_remove_multiple_friend(self):
        self.user1.friends.add(self.user2)
        self.user1.friends.add(self.user3)
        response = self.client1.patch(
            reverse("remove_friends"),
            {"friends": [str(self.user2.id), str(self.user3.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.assertFalse(self.user2 in self.user1.friends.all())
        self.assertFalse(self.user3 in self.user1.friends.all())

    def test_remove_multiple_friend_mutliple_request(self):
        self.user1.friends.add(self.user2)
        self.user1.friends.add(self.user3)
        response = self.client1.patch(
            reverse("remove_friends"),
            {"friends": [str(self.user2.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        response = self.client1.patch(
            reverse("remove_friends"),
            {"friends": [str(self.user3.id)]},
            format="json",
        ) 
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.assertFalse(self.user2 in self.user1.friends.all())
        self.assertFalse(self.user3 in self.user1.friends.all())

    def test_remove_friend_not_friend(self):
        response = self.client1.patch(
            reverse("remove_friends"),
            {"friends": [str(self.user2.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.assertFalse(self.user2 in self.user1.friends.all())

    def test_remove_friend_not_found(self):
        response = self.client1.patch(
            reverse("remove_friends"),
            {"friends": [str(uuid.uuid4())]},
            format="json",
        )
        self.assertNotEqual(response.status_code, 200)

    def test_remove_friend_bad_request(self):
        response = self.client1.patch(
            reverse("remove_friends"),
            {"friends": "bad"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)


class TestCustomUserListView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.fr",
            password="PasSalut12!",
            is_active=True,
        )
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

    def test_customuser_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(reverse("users"))
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_customuser_list_unauthorized(self):
        response = self.client.get(reverse("users"))
        self.assertEqual(response.status_code, 401)

    def test_customuser_list_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.user.is_active = False
        self.user.save()
        response = self.client.get(reverse("users"))
        self.assertEqual(response.status_code, 401)

    def test_customuser_list_bad_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}bad")
        response = self.client.get(reverse("users"))
        self.assertEqual(response.status_code, 401)
