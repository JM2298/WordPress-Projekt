import json
from unittest.mock import Mock, patch

import requests
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class OpenAIProductGenerationApiTests(APITestCase):
    @staticmethod
    def _mock_response(status_code: int, payload):
        response = Mock()
        response.status_code = status_code
        response.json.return_value = payload
        response.text = json.dumps(payload)
        return response

    @override_settings(
        OPENAI_API_KEY="sk-test",
        OPENAI_TEXT_MODEL="gpt-5.4-nano-2026-03-17",
        OPENAI_IMAGE_MODEL="gpt-image-1",
        OPENAI_PRODUCTS_ENDPOINT="http://localhost:18000/api/ecommerce/products/",
        OPENAI_PRODUCTS_TIMEOUT_SECONDS=30,
        OPENAI_DEFAULT_CATEGORY_ID=1,
    )
    @patch("openai_api.services.requests.post")
    @patch("openai_api.services.OpenAI")
    def test_generate_and_create_product(self, openai_mock: Mock, post_mock: Mock) -> None:
        openai_client = Mock()
        openai_mock.return_value = openai_client

        text_response = Mock()
        text_response.output_text = json.dumps(
            {
                "name": "Lavender Dream Soap",
                "type": "simple",
                "regular_price": "39.99",
                "description": "Natural lavender soap with shea butter.",
                "short_description": "Lavender soap for daily care.",
            }
        )
        openai_client.responses.create.return_value = text_response

        image_data = Mock()
        image_data.url = "https://cdn.example.com/lavender-soap.png"
        image_data.b64_json = None
        image_response = Mock()
        image_response.data = [image_data]
        openai_client.images.generate.return_value = image_response

        post_mock.return_value = self._mock_response(
            status.HTTP_201_CREATED,
            {"id": 1001, "name": "Lavender Dream Soap"},
        )

        response = self.client.post(
            reverse("openai-generate-create-product"),
            {
                "prompt": "Natural lavender soap for sensitive skin",
                "regular_price": "39.99",
                "category_ids": [1],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payload = response.json()["generated_payload"]
        self.assertEqual(payload["name"], "Lavender Dream Soap")
        self.assertEqual(payload["images"][0]["src"], "https://cdn.example.com/lavender-soap.png")
        self.assertEqual(payload["categories"], [{"id": 1}])

        post_mock.assert_called_once()
        called = post_mock.call_args.kwargs
        self.assertEqual(
            called["url"] if "url" in called else post_mock.call_args.args[0],
            "http://localhost:18000/api/ecommerce/products/",
        )

    @override_settings(OPENAI_API_KEY="")
    @patch("openai_api.services.OpenAI")
    def test_missing_openai_api_key(self, openai_mock: Mock) -> None:
        response = self.client.post(
            reverse("openai-generate-create-product"),
            {"prompt": "Minimal product"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Missing OPENAI_API_KEY", response.json()["detail"])
        openai_mock.assert_not_called()

    @override_settings(
        OPENAI_API_KEY="sk-test",
        OPENAI_TEXT_MODEL="gpt-5.4-nano-2026-03-17",
        OPENAI_IMAGE_MODEL="gpt-image-1",
        OPENAI_PRODUCTS_ENDPOINT="http://localhost:18000/api/ecommerce/products/",
        OPENAI_PRODUCTS_TIMEOUT_SECONDS=30,
        OPENAI_DEFAULT_CATEGORY_ID=1,
    )
    @patch("openai_api.services.requests.post")
    @patch("openai_api.services.OpenAI")
    def test_fallback_products_endpoint_when_localhost_refused(
        self,
        openai_mock: Mock,
        post_mock: Mock,
    ) -> None:
        openai_client = Mock()
        openai_mock.return_value = openai_client

        text_response = Mock()
        text_response.output_text = json.dumps(
            {
                "name": "Eco Bottle",
                "type": "simple",
                "regular_price": "19.99",
                "description": "Reusable eco bottle.",
                "short_description": "Reusable bottle.",
            }
        )
        openai_client.responses.create.return_value = text_response

        image_data = Mock()
        image_data.url = "https://cdn.example.com/eco-bottle.png"
        image_data.b64_json = None
        image_response = Mock()
        image_response.data = [image_data]
        openai_client.images.generate.return_value = image_response

        post_mock.side_effect = [
            requests.RequestException("connection refused"),
            self._mock_response(
                status.HTTP_201_CREATED,
                {"id": 1002, "name": "Eco Bottle"},
            ),
        ]

        response = self.client.post(
            reverse("openai-generate-create-product"),
            {"prompt": "Reusable eco bottle"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        called_urls = [
            call.kwargs["url"] if "url" in call.kwargs else call.args[0]
            for call in post_mock.call_args_list
        ]
        self.assertEqual(
            called_urls[0],
            "http://localhost:18000/api/ecommerce/products/",
        )
        self.assertEqual(
            called_urls[1],
            "http://localhost:8000/api/ecommerce/products/",
        )
