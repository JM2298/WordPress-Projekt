from __future__ import annotations

import base64
import json
import re
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import requests
from django.conf import settings

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled in runtime configuration error
    OpenAI = None


class OpenAIConfigurationError(Exception):
    """Raised when required OpenAI settings are missing."""


class OpenAIIntegrationError(Exception):
    """Raised when OpenAI or e-commerce API integration fails."""

    def __init__(
        self,
        message: str,
        status_code: int = 502,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class OpenAIProductGenerator:
    def __init__(self) -> None:
        self.api_key = str(getattr(settings, "OPENAI_API_KEY", ""))
        self.text_model = str(
            getattr(settings, "OPENAI_TEXT_MODEL", "gpt-5.4-nano-2026-03-17")
        )
        self.image_model = str(
            getattr(settings, "OPENAI_IMAGE_MODEL", "gpt-image-1-mini")
        )
        self.products_endpoint = str(
            getattr(
                settings,
                "OPENAI_PRODUCTS_ENDPOINT",
                "http://localhost:18000/api/ecommerce/products/",
            )
        )
        self.products_timeout = int(
            getattr(settings, "OPENAI_PRODUCTS_TIMEOUT_SECONDS", 30)
        )
        self.default_category_id = int(getattr(settings, "OPENAI_DEFAULT_CATEGORY_ID", 1))
        self.store_url = str(getattr(settings, "WOOCOMMERCE_STORE_URL", "")).rstrip("/")
        self.public_image_base_url = str(
            getattr(
                settings,
                "OPENAI_GENERATED_IMAGE_PUBLIC_URL_BASE",
                "http://nginx",
            )
        ).rstrip("/")
        self.retry_without_image_on_upload_error = bool(
            getattr(settings, "OPENAI_RETRY_WITHOUT_IMAGE_ON_UPLOAD_ERROR", True)
        )

    def _build_client(self):
        if OpenAI is None:
            raise OpenAIConfigurationError(
                "Missing dependency: openai. Install packages from requirements.txt."
            )

        if not self.api_key:
            raise OpenAIConfigurationError("Missing OPENAI_API_KEY setting.")

        return OpenAI(api_key=self.api_key)

    @staticmethod
    def _extract_json_object(text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if cleaned:
            try:
                data = json.loads(cleaned)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass

        matches = re.findall(r"\{.*\}", text, flags=re.DOTALL)
        for candidate in matches:
            try:
                data = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                return data

        raise OpenAIIntegrationError(
            "OpenAI text response could not be parsed as JSON.",
            status_code=502,
            details={"output_text": text},
        )

    def _generate_text_payload(
        self,
        prompt: str,
        product_type: str,
        regular_price: str,
    ) -> dict[str, str]:
        client = self._build_client()

        response = client.responses.create(
            model=self.text_model,
            input=(
                "Create a WooCommerce product payload and return ONLY valid JSON. "
                "The JSON must include keys: name, type, regular_price, description, "
                "short_description. "
                f"Product brief: {prompt}. "
                f"Preferred product type: {product_type}. "
                f"Preferred regular_price: {regular_price}."
            ),
        )

        output_text = str(getattr(response, "output_text", "") or "")
        payload = self._extract_json_object(output_text)

        fallback_price = regular_price or "19.99"
        return {
            "name": str(payload.get("name") or prompt[:80]).strip(),
            "type": str(payload.get("type") or product_type or "simple").strip(),
            "regular_price": str(payload.get("regular_price") or fallback_price).strip(),
            "description": str(payload.get("description") or "").strip(),
            "short_description": str(payload.get("short_description") or "").strip(),
        }

    def _build_public_image_url(self, base_url: str, filename: str) -> str:
        media_prefix = str(getattr(settings, "MEDIA_URL", "/media/")).strip("/")
        return f"{base_url.rstrip('/')}/{media_prefix}/generated-products/{filename}"

    def _candidate_image_base_urls(self) -> list[str]:
        candidates: list[str] = []
        configured_base = self.public_image_base_url.strip()
        if configured_base:
            candidates.append(configured_base)

        store_url = self.store_url.strip()
        if store_url:
            parsed_store = urlsplit(store_url)
            if parsed_store.scheme and parsed_store.hostname:
                store_host = parsed_store.hostname
                store_scheme = parsed_store.scheme

                if parsed_store.port:
                    candidates.append(
                        f"{store_scheme}://{store_host}:{parsed_store.port}"
                    )
                else:
                    candidates.append(f"{store_scheme}://{store_host}")

                if configured_base:
                    parsed_base = urlsplit(configured_base)
                    if parsed_base.port:
                        candidates.append(
                            f"{store_scheme}://{store_host}:{parsed_base.port}"
                        )

        candidates.extend(
            [
                "http://nginx",
                "http://host.docker.internal:18000",
                "http://host.docker.internal:18001",
                "http://host.docker.internal:8888",
            ]
        )

        unique_candidates: list[str] = []
        for candidate in candidates:
            if candidate and candidate not in unique_candidates:
                unique_candidates.append(candidate)
        return unique_candidates

    def _candidate_image_urls(self, filename: str) -> list[str]:
        return [
            self._build_public_image_url(base_url=base_url, filename=filename)
            for base_url in self._candidate_image_base_urls()
        ]

    def _save_image_base64(self, b64_content: str) -> str:
        image_dir = Path(getattr(settings, "MEDIA_ROOT")) / "generated-products"
        image_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4().hex}.png"
        image_path = image_dir / filename

        try:
            image_bytes = base64.b64decode(b64_content)
        except (ValueError, TypeError) as exc:
            raise OpenAIIntegrationError(
                "OpenAI image response returned invalid base64 data.",
                status_code=502,
            ) from exc

        image_path.write_bytes(image_bytes)
        return filename

    def _generate_image_sources(self, prompt: str) -> list[str]:
        client = self._build_client()
        image_response = client.images.generate(
            model=self.image_model,
            prompt=(
                "High-quality ecommerce product photo on a clean background. "
                f"Product brief: {prompt}."
            ),
            size="1024x1024",
            quality="low",
        )

        images = getattr(image_response, "data", None) or []
        if not images:
            raise OpenAIIntegrationError(
                "OpenAI image generation returned an empty response.",
                status_code=502,
            )

        first_image = images[0]
        remote_url = getattr(first_image, "url", None)
        if remote_url:
            return [str(remote_url)]

        b64_content = getattr(first_image, "b64_json", None)
        if not b64_content:
            raise OpenAIIntegrationError(
                "OpenAI image generation did not return image URL or base64 content.",
                status_code=502,
            )

        filename = self._save_image_base64(str(b64_content))
        return self._candidate_image_urls(filename=filename)

    def _candidate_products_endpoints(self) -> list[str]:
        endpoint = self.products_endpoint.strip()
        if not endpoint:
            return []

        candidates: list[str] = [endpoint]
        parsed = urlsplit(endpoint)
        hostname = parsed.hostname
        if not hostname:
            return candidates

        def with_host_port(host: str, port: int | None) -> str:
            netloc = host if port is None else f"{host}:{port}"
            return urlunsplit(
                (
                    parsed.scheme,
                    netloc,
                    parsed.path,
                    parsed.query,
                    parsed.fragment,
                )
            )

        if hostname in {"localhost", "127.0.0.1"}:
            if parsed.port == 18000:
                candidates.extend(
                    [
                        with_host_port("localhost", 8000),
                        with_host_port("django", 8000),
                        with_host_port("host.docker.internal", 18000),
                    ]
                )
            else:
                candidates.append(with_host_port("django", parsed.port))

        unique_candidates: list[str] = []
        for candidate in candidates:
            if candidate not in unique_candidates:
                unique_candidates.append(candidate)
        return unique_candidates

    def _post_product(self, payload: dict[str, Any]) -> Any:
        attempts: list[dict[str, str]] = []
        endpoints = self._candidate_products_endpoints()
        if not endpoints:
            raise OpenAIConfigurationError("Missing OPENAI_PRODUCTS_ENDPOINT setting.")

        for endpoint in endpoints:
            try:
                response = requests.post(
                    endpoint,
                    json=payload,
                    timeout=self.products_timeout,
                )
            except requests.RequestException as exc:
                attempts.append({"url": endpoint, "error": str(exc)})
                continue

            try:
                data = response.json()
            except ValueError:
                data = None

            if response.status_code >= 400:
                details = data if data is not None else {"message": response.text}
                raise OpenAIIntegrationError(
                    "Ecommerce products API returned an error.",
                    status_code=response.status_code,
                    details={"url": endpoint, "response": details},
                )

            if data is None:
                raise OpenAIIntegrationError(
                    "Ecommerce products API returned invalid JSON.",
                    status_code=502,
                    details={"url": endpoint},
                )

            return data

        raise OpenAIIntegrationError(
            "Unable to connect to ecommerce products API.",
            status_code=502,
            details={"attempts": attempts},
        )

    @staticmethod
    def _is_woocommerce_image_upload_error(exc: OpenAIIntegrationError) -> bool:
        details = exc.details if isinstance(exc.details, dict) else {}
        response_payload = details.get("response")
        if not isinstance(response_payload, dict):
            return False

        error_payload = response_payload.get("error")
        if not isinstance(error_payload, dict):
            return False

        return error_payload.get("code") == "woocommerce_product_image_upload_error"

    @staticmethod
    def _is_local_image_url_validation_error(exc: OpenAIIntegrationError) -> bool:
        details = exc.details if isinstance(exc.details, dict) else {}
        response_payload = details.get("response")
        if not isinstance(response_payload, dict):
            return False

        image_errors = response_payload.get("images")
        if not isinstance(image_errors, list):
            return False

        for item in image_errors:
            if isinstance(item, dict) and "src" in item:
                return True

        return False

    def generate_and_create_product(
        self,
        prompt: str,
        type: str = "simple",
        regular_price: str = "",
        category_ids: list[int] | None = None,
    ) -> dict[str, Any]:
        product_copy = self._generate_text_payload(
            prompt=prompt,
            product_type=type,
            regular_price=regular_price,
        )
        image_sources = self._generate_image_sources(prompt=prompt)

        categories = category_ids or [self.default_category_id]
        base_payload: dict[str, Any] = {
            **product_copy,
            "categories": [{"id": category_id} for category_id in categories],
        }
        image_attempt_errors: list[dict[str, Any]] = []

        for image_src in image_sources:
            payload = {**base_payload, "images": [{"src": image_src}]}
            try:
                ecommerce_response = self._post_product(payload=payload)
                return {
                    "generated_payload": payload,
                    "ecommerce_response": ecommerce_response,
                }
            except OpenAIIntegrationError as exc:
                if self._is_woocommerce_image_upload_error(
                    exc
                ) or self._is_local_image_url_validation_error(exc):
                    image_attempt_errors.append(
                        {
                            "image_src": image_src,
                            "error": exc.details,
                        }
                    )
                    continue
                raise

        if self.retry_without_image_on_upload_error:
            payload_without_images = dict(base_payload)
            ecommerce_response = self._post_product(payload=payload_without_images)
            return {
                "generated_payload": payload_without_images,
                "ecommerce_response": ecommerce_response,
                "warnings": [
                    {
                        "code": "image_upload_failed",
                        "message": "Product created without image after image URL retries.",
                        "attempts": image_attempt_errors,
                    }
                ],
            }

        if image_attempt_errors:
            raise OpenAIIntegrationError(
                "WooCommerce rejected all generated image URLs.",
                status_code=400,
                details={"attempts": image_attempt_errors},
            )

        raise OpenAIIntegrationError(
            "Image generation did not return usable image URLs.",
            status_code=502,
        )
