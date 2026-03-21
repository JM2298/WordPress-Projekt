from typing import Any
from urllib.parse import parse_qsl, urlparse, urlsplit, urlunsplit

import requests
from django.conf import settings
from oauthlib.oauth1 import Client, SIGNATURE_HMAC_SHA256, SIGNATURE_TYPE_QUERY


class WooCommerceConfigurationError(Exception):
    """Raised when required WooCommerce settings are missing."""


class WooCommerceAPIError(Exception):
    """Raised when WooCommerce returns an API or transport error."""

    def __init__(
        self,
        message: str,
        status_code: int = 502,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class WooCommerceClient:
    def __init__(self) -> None:
        self.base_url = str(getattr(settings, "WOOCOMMERCE_STORE_URL", "")).rstrip("/")
        self.consumer_key = str(getattr(settings, "WOOCOMMERCE_CONSUMER_KEY", ""))
        self.consumer_secret = str(
            getattr(settings, "WOOCOMMERCE_CONSUMER_SECRET", "")
        )
        self.timeout = int(getattr(settings, "WOOCOMMERCE_TIMEOUT_SECONDS", 15))
        self.auth_method = str(
            getattr(settings, "WOOCOMMERCE_AUTH_METHOD", "auto")
        ).lower()
        self.signature_base_url = str(
            getattr(settings, "WOOCOMMERCE_SIGNATURE_BASE_URL", "")
        ).rstrip("/")

    def _validate_configuration(self) -> None:
        missing = []
        if not self.base_url:
            missing.append("WOOCOMMERCE_STORE_URL")
        if not self.consumer_key:
            missing.append("WOOCOMMERCE_CONSUMER_KEY")
        if not self.consumer_secret:
            missing.append("WOOCOMMERCE_CONSUMER_SECRET")

        if missing:
            raise WooCommerceConfigurationError(
                f"Missing WooCommerce settings: {', '.join(missing)}."
            )

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/wp-json/wc/v3/{path.lstrip('/')}"

    def _build_url_for_base(self, base_url: str, path: str) -> str:
        return f"{base_url.rstrip('/')}/wp-json/wc/v3/{path.lstrip('/')}"

    def _resolved_auth_method(self, base_url: str | None = None) -> str:
        target_base_url = base_url or self.base_url
        if self.auth_method in {"query", "basic", "oauth1"}:
            return self.auth_method
        if target_base_url.startswith("https://"):
            return "basic"
        return "oauth1"

    def _auth_kwargs(
        self,
        method: str,
        path: str,
        base_url: str,
        auth_method_override: str | None = None,
    ) -> dict[str, Any]:
        auth_method = auth_method_override or self._resolved_auth_method(
            base_url=base_url
        )
        if auth_method == "query":
            return {
                "params": {
                    "consumer_key": self.consumer_key,
                    "consumer_secret": self.consumer_secret,
                }
            }
        if auth_method == "basic":
            return {"auth": (self.consumer_key, self.consumer_secret)}

        signature_base = self.signature_base_url or base_url

        signature_url = f"{signature_base}/wp-json/wc/v3/{path.lstrip('/')}"
        client = Client(
            client_key=self.consumer_key,
            client_secret=self.consumer_secret,
            signature_method=SIGNATURE_HMAC_SHA256,
            signature_type=SIGNATURE_TYPE_QUERY,
        )
        signed_uri, _, _ = client.sign(
            signature_url,
            http_method=method.upper(),
        )
        return {"params": dict(parse_qsl(urlparse(signed_uri).query))}

    @staticmethod
    def _is_invalid_signature_error(exc: WooCommerceAPIError) -> bool:
        if exc.status_code != 401:
            return False

        details = exc.details if isinstance(exc.details, dict) else {}
        code = details.get("code")
        if code != "woocommerce_rest_authentication_error":
            return False

        message = str(details.get("message", "")).lower()
        return "podpis" in message or "signature" in message

    def _candidate_base_urls(self) -> list[str]:
        base = self.base_url.strip()
        if not base:
            return []

        candidates: list[str] = [base]
        parsed = urlsplit(base)
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
            ).rstrip("/")

        if hostname in {"localhost", "127.0.0.1"}:
            if parsed.port == 8888:
                candidates.extend(
                    [
                        with_host_port("nginx", 80),
                        with_host_port("host.docker.internal", 8888),
                    ]
                )
            else:
                candidates.extend(
                    [
                        with_host_port("nginx", 80),
                        with_host_port("host.docker.internal", parsed.port),
                    ]
                )

        unique_candidates: list[str] = []
        for candidate in candidates:
            if candidate and candidate not in unique_candidates:
                unique_candidates.append(candidate)
        return unique_candidates

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        self._validate_configuration()
        attempts: list[dict[str, str]] = []
        candidate_urls = self._candidate_base_urls()
        if not candidate_urls:
            raise WooCommerceConfigurationError("Missing WOOCOMMERCE_STORE_URL setting.")

        for base_url in candidate_urls:
            query_params = dict(params or {})
            resolved_auth_method = self._resolved_auth_method(base_url=base_url)
            auth_kwargs = self._auth_kwargs(
                method=method,
                path=path,
                base_url=base_url,
                auth_method_override=resolved_auth_method,
            )
            if "params" in auth_kwargs:
                query_params.update(auth_kwargs["params"])

            try:
                response = requests.request(
                    method=method,
                    url=self._build_url_for_base(base_url=base_url, path=path),
                    json=payload,
                    params=query_params,
                    auth=auth_kwargs.get("auth"),
                    timeout=self.timeout,
                )
            except requests.RequestException as exc:
                attempts.append({"url": base_url, "error": str(exc)})
                continue

            try:
                return self._handle_response(response)
            except WooCommerceAPIError as exc:
                if (
                    resolved_auth_method == "oauth1"
                    and self._is_invalid_signature_error(exc)
                ):
                    retry_params = dict(params or {})
                    retry_auth_kwargs = self._auth_kwargs(
                        method=method,
                        path=path,
                        base_url=base_url,
                        auth_method_override="query",
                    )
                    if "params" in retry_auth_kwargs:
                        retry_params.update(retry_auth_kwargs["params"])

                    try:
                        retry_response = requests.request(
                            method=method,
                            url=self._build_url_for_base(base_url=base_url, path=path),
                            json=payload,
                            params=retry_params,
                            auth=retry_auth_kwargs.get("auth"),
                            timeout=self.timeout,
                        )
                    except requests.RequestException as retry_exc:
                        attempts.append(
                            {
                                "url": base_url,
                                "error": str(retry_exc),
                            }
                        )
                        continue

                    try:
                        return self._handle_response(retry_response)
                    except WooCommerceAPIError as retry_error:
                        if retry_error.details is None:
                            retry_error.details = {}
                        if isinstance(retry_error.details, dict):
                            retry_error.details.setdefault("url", base_url)
                            retry_error.details.setdefault(
                                "auth_fallback",
                                "query",
                            )
                        raise

                if exc.details is None:
                    exc.details = {}
                if isinstance(exc.details, dict):
                    exc.details.setdefault("url", base_url)
                raise

        raise WooCommerceAPIError(
            "Unable to connect to WooCommerce.",
            status_code=502,
            details={"attempts": attempts},
        )

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            data = None

        if response.status_code >= 400:
            details = data if data is not None else {"message": response.text}
            raise WooCommerceAPIError(
                "WooCommerce returned an error.",
                status_code=response.status_code,
                details=details,
            )

        if data is None:
            raise WooCommerceAPIError(
                "WooCommerce returned an invalid JSON response.",
                status_code=502,
            )

        return data

    def create_category(self, payload: dict[str, Any]) -> Any:
        return self._request("POST", "products/categories", payload=payload)

    def create_product(self, payload: dict[str, Any]) -> Any:
        return self._request("POST", "products", payload=payload)

    def list_products(self) -> Any:
        return self._request("GET", "products")

    def get_product(self, product_id: int) -> Any:
        return self._request("GET", f"products/{product_id}")
