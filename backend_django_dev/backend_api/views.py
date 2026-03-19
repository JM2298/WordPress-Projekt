from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    PingSerializer,
    RegisterResponseSerializer,
    RegisterSerializer,
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
