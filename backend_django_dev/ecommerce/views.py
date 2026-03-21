import logging

from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .notifications import send_product_created_email
from .sheets import append_product_to_sheet
from .serializers import CategoryCreateSerializer, ProductCreateSerializer
from .services import (
    WooCommerceAPIError,
    WooCommerceClient,
    WooCommerceConfigurationError,
)

logger = logging.getLogger(__name__)


def _error_response(exc: Exception) -> Response:
    if isinstance(exc, WooCommerceConfigurationError):
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, WooCommerceAPIError):
        payload = {"detail": str(exc)}
        if exc.details is not None:
            payload["error"] = exc.details
        return Response(payload, status=exc.status_code)

    return Response(
        {"detail": "Unexpected WooCommerce integration error."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@extend_schema(
    request=CategoryCreateSerializer,
    responses={201: OpenApiTypes.OBJECT},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def create_category(request: Request) -> Response:
    serializer = CategoryCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    client = WooCommerceClient()
    try:
        response_data = client.create_category(serializer.validated_data)
    except (WooCommerceConfigurationError, WooCommerceAPIError) as exc:
        return _error_response(exc)

    return Response(response_data, status=status.HTTP_201_CREATED)


@extend_schema(
    request=ProductCreateSerializer,
    responses={200: OpenApiTypes.OBJECT, 201: OpenApiTypes.OBJECT},
)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def products(request: Request) -> Response:
    client = WooCommerceClient()

    try:
        if request.method == "GET":
            response_data = client.list_products()
            return Response(response_data, status=status.HTTP_200_OK)

        serializer = ProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = client.create_product(serializer.validated_data)

        try:
            notified = send_product_created_email(response_data)
            logger.info("Product notification email sent to %s users.", notified)
        except Exception:
            logger.exception("Unable to send product-created notification emails.")

        try:
            append_result = append_product_to_sheet(response_data)
            logger.info(
                "Product synchronized to Google Sheets. updates=%s",
                append_result.get("updates"),
            )
        except Exception:
            logger.exception("Unable to synchronize product to Google Sheets.")

        return Response(response_data, status=status.HTTP_201_CREATED)
    except (WooCommerceConfigurationError, WooCommerceAPIError) as exc:
        return _error_response(exc)


@extend_schema(
    responses={200: OpenApiTypes.OBJECT},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def product_detail(_: Request, product_id: int) -> Response:
    client = WooCommerceClient()
    try:
        response_data = client.get_product(product_id=product_id)
    except (WooCommerceConfigurationError, WooCommerceAPIError) as exc:
        return _error_response(exc)

    return Response(response_data, status=status.HTTP_200_OK)
