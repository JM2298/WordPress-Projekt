from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .google_sheets import GoogleSheetsAPIError, GoogleSheetsConfigurationError


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

    @patch("backend_api.views.read_sheet")
    def test_get_sheet_data(self, read_sheet_mock) -> None:
        read_sheet_mock.return_value = [
            ["Jan", "Kowalski", "jan@example.com", "OK"],
        ]

        response = self.client.get(
            reverse("sheets-data"),
            {"range_name": "Arkusz1!A1:D20"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {"rows": [["Jan", "Kowalski", "jan@example.com", "OK"]]},
        )
        read_sheet_mock.assert_called_once_with(range_name="Arkusz1!A1:D20")

    @patch("backend_api.views.append_row")
    def test_save_to_sheet(self, append_row_mock) -> None:
        append_row_mock.return_value = {"updates": {"updatedRows": 1}}

        response = self.client.post(
            reverse("save-to-sheet"),
            {
                "row": ["Jan", "Kowalski", "jan@example.com", "OK"],
                "range_name": "Arkusz1!A:D",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "saved")
        self.assertIn("result", response.data)
        append_row_mock.assert_called_once_with(
            row=["Jan", "Kowalski", "jan@example.com", "OK"],
            range_name="Arkusz1!A:D",
        )

    @patch("backend_api.views.read_sheet")
    def test_get_sheet_data_configuration_error(self, read_sheet_mock) -> None:
        read_sheet_mock.side_effect = GoogleSheetsConfigurationError(
            "Missing GOOGLE_SHEET_ID setting."
        )

        response = self.client.get(reverse("sheets-data"))

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["detail"], "Missing GOOGLE_SHEET_ID setting.")

    @patch("backend_api.views.append_row")
    def test_save_to_sheet_api_error(self, append_row_mock) -> None:
        append_row_mock.side_effect = GoogleSheetsAPIError(
            "Google Sheets API returned an error while appending a row.",
            status_code=403,
            details={"response": {"error": {"status": "PERMISSION_DENIED"}}},
        )

        response = self.client.post(
            reverse("sheets-append"),
            {"row": ["Jan", "Kowalski"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "Google Sheets API returned an error while appending a row.",
        )
        self.assertIn("error", response.data)
