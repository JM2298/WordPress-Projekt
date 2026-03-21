from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import ProductGenerationRequestSerializer
from .services import (
    OpenAIConfigurationError,
    OpenAIIntegrationError,
    OpenAIProductGenerator,
)


def _error_response(exc: Exception) -> Response:
    if isinstance(exc, OpenAIConfigurationError):
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, OpenAIIntegrationError):
        payload = {"detail": str(exc)}
        if exc.details is not None:
            payload["error"] = exc.details
        return Response(payload, status=exc.status_code)

    return Response(
        {"detail": "Unexpected OpenAI integration error."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@extend_schema(
    request=ProductGenerationRequestSerializer,
    responses={201: OpenApiTypes.OBJECT},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def generate_and_create_product(request: Request) -> Response:
    serializer = ProductGenerationRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    service = OpenAIProductGenerator()
    try:
        result = service.generate_and_create_product(**serializer.validated_data)
    except (OpenAIConfigurationError, OpenAIIntegrationError) as exc:
        return _error_response(exc)

    return Response(result, status=status.HTTP_201_CREATED)
