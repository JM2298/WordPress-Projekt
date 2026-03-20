from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from rest_framework.permissions import AllowAny


def health(_: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("api/", include("backend_api.urls")),
    path("api/ecommerce/", include("ecommerce.urls")),
    path(
        "api/schema/",
        SpectacularAPIView.as_view(permission_classes=[AllowAny]),
        name="api-schema",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(
            permission_classes=[AllowAny],
            url_name="api-schema",
        ),
        name="api-redoc",
    ),
]
