import json
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class EcommerceApiTests(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="ecommerce-user",
            email="ecommerce@example.com",
            password="strong-pass-123",
        )
        self.client.force_authenticate(user=self.user)

    @staticmethod
    def _mock_response(status_code: int, payload):
        response = Mock()
        response.status_code = status_code
        response.json.return_value = payload
        response.text = json.dumps(payload)
        return response

    @override_settings(
        WOOCOMMERCE_STORE_URL="https://shop.example.com",
        WOOCOMMERCE_CONSUMER_KEY="ck_test",
        WOOCOMMERCE_CONSUMER_SECRET="cs_test",
        WOOCOMMERCE_TIMEOUT_SECONDS=15,
    )
    @patch("ecommerce.services.requests.request")
    def test_create_category_without_authentication(self, request_mock: Mock) -> None:
        self.client.force_authenticate(user=None)
        request_mock.return_value = self._mock_response(
            status.HTTP_201_CREATED,
            {"id": 99, "name": "Clothing"},
        )

        response = self.client.post(
            reverse("ecommerce-category-create"),
            {"name": "Clothing"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @override_settings(
        WOOCOMMERCE_STORE_URL="https://shop.example.com",
        WOOCOMMERCE_CONSUMER_KEY="ck_test",
        WOOCOMMERCE_CONSUMER_SECRET="cs_test",
        WOOCOMMERCE_TIMEOUT_SECONDS=15,
    )
    @patch("ecommerce.services.requests.request")
    def test_create_category(self, request_mock: Mock) -> None:
        request_mock.return_value = self._mock_response(
            status.HTTP_201_CREATED,
            {"id": 99, "name": "Clothing"},
        )

        payload = {
            "name": "Clothing",
            "image": {
                "src": "https://example.com/category.jpg",
            },
        }

        response = self.client.post(
            reverse("ecommerce-category-create"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {"id": 99, "name": "Clothing"})

        request_mock.assert_called_once()
        called_kwargs = request_mock.call_args.kwargs
        self.assertEqual(called_kwargs["method"], "POST")
        self.assertEqual(
            called_kwargs["url"],
            "https://shop.example.com/wp-json/wc/v3/products/categories",
        )
        self.assertEqual(called_kwargs["json"], payload)
        self.assertEqual(called_kwargs["auth"], ("ck_test", "cs_test"))

    @override_settings(
        WOOCOMMERCE_STORE_URL="https://shop.example.com",
        WOOCOMMERCE_CONSUMER_KEY="ck_test",
        WOOCOMMERCE_CONSUMER_SECRET="cs_test",
    )
    @patch("ecommerce.services.requests.request")
    def test_create_product(self, request_mock: Mock) -> None:
        request_mock.return_value = self._mock_response(
            status.HTTP_201_CREATED,
            {"id": 42, "name": "Premium Quality"},
        )

        payload = {
            "name": "Premium Quality",
            "type": "simple",
            "regular_price": "21.99",
            "description": "Sample description",
            "short_description": "Sample short description",
            "categories": [{"id": 9}, {"id": 14}],
            "images": [{"id": 42}],
        }

        response = self.client.post(
            reverse("ecommerce-products"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["id"], 42)

        called_kwargs = request_mock.call_args.kwargs
        self.assertEqual(called_kwargs["method"], "POST")
        self.assertEqual(
            called_kwargs["url"],
            "https://shop.example.com/wp-json/wc/v3/products",
        )
        self.assertEqual(called_kwargs["json"], payload)
        self.assertEqual(called_kwargs["auth"], ("ck_test", "cs_test"))

    @override_settings(
        WOOCOMMERCE_STORE_URL="https://shop.example.com",
        WOOCOMMERCE_CONSUMER_KEY="ck_test",
        WOOCOMMERCE_CONSUMER_SECRET="cs_test",
    )
    @patch("ecommerce.services.requests.request")
    def test_list_products(self, request_mock: Mock) -> None:
        request_mock.return_value = self._mock_response(
            status.HTTP_200_OK,
            [{"id": 1, "name": "Product 1"}],
        )

        response = self.client.get(reverse("ecommerce-products"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [{"id": 1, "name": "Product 1"}])

        called_kwargs = request_mock.call_args.kwargs
        self.assertEqual(called_kwargs["method"], "GET")
        self.assertEqual(
            called_kwargs["url"],
            "https://shop.example.com/wp-json/wc/v3/products",
        )
        self.assertEqual(called_kwargs["auth"], ("ck_test", "cs_test"))

    @override_settings(
        WOOCOMMERCE_STORE_URL="https://shop.example.com",
        WOOCOMMERCE_CONSUMER_KEY="ck_test",
        WOOCOMMERCE_CONSUMER_SECRET="cs_test",
    )
    @patch("ecommerce.services.requests.request")
    def test_get_product_detail(self, request_mock: Mock) -> None:
        request_mock.return_value = self._mock_response(
            status.HTTP_200_OK,
            {"id": 321, "name": "Single Product"},
        )

        response = self.client.get(reverse("ecommerce-product-detail", args=[321]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], 321)

        called_kwargs = request_mock.call_args.kwargs
        self.assertEqual(called_kwargs["method"], "GET")
        self.assertEqual(
            called_kwargs["url"],
            "https://shop.example.com/wp-json/wc/v3/products/321",
        )
        self.assertEqual(called_kwargs["auth"], ("ck_test", "cs_test"))

    @override_settings(
        WOOCOMMERCE_STORE_URL="http://shop.example.com",
        WOOCOMMERCE_CONSUMER_KEY="ck_test",
        WOOCOMMERCE_CONSUMER_SECRET="cs_test",
        WOOCOMMERCE_AUTH_METHOD="auto",
    )
    @patch("ecommerce.services.requests.request")
    def test_http_store_uses_oauth1(self, request_mock: Mock) -> None:
        request_mock.return_value = self._mock_response(
            status.HTTP_200_OK,
            [{"id": 1, "name": "Product 1"}],
        )

        response = self.client.get(reverse("ecommerce-products"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        called_kwargs = request_mock.call_args.kwargs
        self.assertIsNone(called_kwargs.get("auth"))
        self.assertIn("oauth_consumer_key", called_kwargs["params"])
        self.assertIn("oauth_signature", called_kwargs["params"])
        self.assertEqual(called_kwargs["params"]["oauth_consumer_key"], "ck_test")

    @override_settings(
        WOOCOMMERCE_STORE_URL="",
        WOOCOMMERCE_CONSUMER_KEY="",
        WOOCOMMERCE_CONSUMER_SECRET="",
    )
    @patch("ecommerce.services.requests.request")
    def test_missing_woocommerce_settings(self, request_mock: Mock) -> None:
        response = self.client.get(reverse("ecommerce-products"))

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Missing WooCommerce settings", response.json()["detail"])
        request_mock.assert_not_called()
