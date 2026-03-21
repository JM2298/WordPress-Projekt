from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import get_sheet_data, me, ping, register, save_to_sheet

urlpatterns = [
    path("ping/", ping, name="backend-api-ping"),
    path("me/", me, name="backend-api-me"),
    path("auth/register/", register, name="auth-register"),
    path("sheets/data/", get_sheet_data, name="sheets-data"),
    path("sheets/append/", save_to_sheet, name="sheets-append"),
    path("save-to-sheet/", save_to_sheet, name="save-to-sheet"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
