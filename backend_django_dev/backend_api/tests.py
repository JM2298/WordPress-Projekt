from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class BackendApiTests(APITestCase):
    def test_ping(self) -> None:
        response = self.client.get(reverse("backend-api-ping"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {"service": "backend_api", "status": "ok"},
        )

    def test_me_requires_authentication(self) -> None:
        response = self.client.get(reverse("backend-api-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_login_and_me(self) -> None:
        user = get_user_model().objects.create_user(
            username="testuser",
            password="strong-pass-123",
            email="test@example.com",
        )

        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testuser", "password": "strong-pass-123"},
            format="json",
        )

        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", token_response.data)
        self.assertIn("refresh", token_response.data)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )
        me_response = self.client.get(reverse("backend-api-me"))

        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            me_response.json(),
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        )

    def test_register_creates_user_and_returns_tokens(self) -> None:
        response = self.client.post(
            reverse("auth-register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "strong-pass-123",
                "password_confirm": "strong-pass-123",
                "first_name": "Jan",
                "last_name": "Kowalski",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

        user = get_user_model().objects.get(username="newuser")
        self.assertEqual(user.email, "new@example.com")
        self.assertEqual(response.data["user"]["id"], user.id)

    def test_register_rejects_password_mismatch(self) -> None:
        response = self.client.post(
            reverse("auth-register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "strong-pass-123",
                "password_confirm": "different-pass-123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)

    def test_register_rejects_duplicate_email(self) -> None:
        get_user_model().objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="strong-pass-123",
        )

        response = self.client.post(
            reverse("auth-register"),
            {
                "username": "newuser",
                "email": "existing@example.com",
                "password": "strong-pass-123",
                "password_confirm": "strong-pass-123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_schema_is_public(self) -> None:
        response = self.client.get(
            reverse("api-schema"),
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("openapi", response.json())

    def test_redoc_is_public(self) -> None:
        response = self.client.get(reverse("api-redoc"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
