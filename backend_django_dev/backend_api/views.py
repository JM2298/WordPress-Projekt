from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .google_sheets import (
    GoogleSheetsAPIError,
    GoogleSheetsConfigurationError,
    append_row,
    read_sheet,
)
from .serializers import (
    PingSerializer,
    RegisterResponseSerializer,
    RegisterSerializer,
    SheetAppendRequestSerializer,
    SheetAppendResponseSerializer,
    SheetReadQuerySerializer,
    SheetReadResponseSerializer,
    UserPublicSerializer,
)


@extend_schema(responses=PingSerializer)
@api_view(["GET"])
@permission_classes([AllowAny])
def ping(_: Request) -> Response:
    return Response({"service": "backend_api", "status": "ok"})


@extend_schema(responses=UserPublicSerializer)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request: Request) -> Response:
    return Response(
        {
            "id": request.user.id,
            "username": request.user.get_username(),
            "email": request.user.email,
        }
    )


@extend_schema(
    request=RegisterSerializer,
    responses={201: RegisterResponseSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request: Request) -> Response:
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "user": {
                "id": user.id,
                "username": user.get_username(),
                "email": user.email,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        },
        status=status.HTTP_201_CREATED,
    )


def _google_sheets_error_response(exc: Exception) -> Response:
    if isinstance(exc, GoogleSheetsConfigurationError):
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, GoogleSheetsAPIError):
        payload = {"detail": str(exc)}
        if exc.details is not None:
            payload["error"] = exc.details
        return Response(payload, status=exc.status_code)

    return Response(
        {"detail": "Unexpected Google Sheets integration error."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@extend_schema(
    parameters=[SheetReadQuerySerializer],
    responses={200: SheetReadResponseSerializer},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_sheet_data(request: Request) -> Response:
    serializer = SheetReadQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    try:
        rows = read_sheet(range_name=serializer.validated_data["range_name"])
    except (GoogleSheetsConfigurationError, GoogleSheetsAPIError) as exc:
        return _google_sheets_error_response(exc)

    return Response({"rows": rows}, status=status.HTTP_200_OK)


@extend_schema(
    request=SheetAppendRequestSerializer,
    responses={200: SheetAppendResponseSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def save_to_sheet(request: Request) -> Response:
    serializer = SheetAppendRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        result = append_row(
            row=serializer.validated_data["row"],
            range_name=serializer.validated_data["range_name"],
        )
    except (GoogleSheetsConfigurationError, GoogleSheetsAPIError) as exc:
        return _google_sheets_error_response(exc)

    return Response(
        {"status": "saved", "result": result},
        status=status.HTTP_200_OK,
    )
