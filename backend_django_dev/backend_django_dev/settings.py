import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
# Load example defaults first, then local overrides from .env.
load_dotenv(BASE_DIR / ".env.example")
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
DEBUG = True
ALLOWED_HOSTS = [host for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",") if host]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "django_extensions",
    "django_celery_beat",
    "channels",
    "backend_api.apps.BackendApiConfig",
    "ecommerce.apps.EcommerceConfig",
    "openai_api.apps.OpenaiApiConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend_django_dev.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend_django_dev.wsgi.application"
ASGI_APPLICATION = "backend_django_dev.asgi.application"

DATABASES = {
    "default": dj_database_url.parse(
        os.getenv("DATABASE_URL", "postgres://app:app@postgres:5432/app"),
        conn_max_age=600,
    )
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TZ", "Europe/Warsaw")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "1") == "1"

CHANNEL_REDIS_URL = os.getenv("CHANNEL_REDIS_URL", os.getenv("REDIS_URL", "redis://redis:6379/0"))
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [CHANNEL_REDIS_URL],
        },
    },
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("JWT_ACCESS_MINUTES", "60"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("JWT_REFRESH_DAYS", "7"))
    ),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Backend Django Dev API",
    "DESCRIPTION": "API documentation",
    "VERSION": "1.0.0",
}

WOOCOMMERCE_STORE_URL = os.getenv("WOOCOMMERCE_STORE_URL", "").rstrip("/")
WOOCOMMERCE_CONSUMER_KEY = os.getenv("WOOCOMMERCE_CONSUMER_KEY", "")
WOOCOMMERCE_CONSUMER_SECRET = os.getenv("WOOCOMMERCE_CONSUMER_SECRET", "")
WOOCOMMERCE_TIMEOUT_SECONDS = int(os.getenv("WOOCOMMERCE_TIMEOUT_SECONDS", "15"))
WOOCOMMERCE_AUTH_METHOD = os.getenv("WOOCOMMERCE_AUTH_METHOD", "auto").lower()
WOOCOMMERCE_SIGNATURE_BASE_URL = os.getenv("WOOCOMMERCE_SIGNATURE_BASE_URL", "").rstrip("/")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-5.4-nano-2026-03-17")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1-mini")
OPENAI_PRODUCTS_ENDPOINT = os.getenv(
    "OPENAI_PRODUCTS_ENDPOINT",
    "http://localhost:18000/api/ecommerce/products/",
)
OPENAI_PRODUCTS_TIMEOUT_SECONDS = int(
    os.getenv("OPENAI_PRODUCTS_TIMEOUT_SECONDS", "30")
)
OPENAI_DEFAULT_CATEGORY_ID = int(os.getenv("OPENAI_DEFAULT_CATEGORY_ID", "1"))
OPENAI_GENERATED_IMAGE_PUBLIC_URL_BASE = os.getenv(
    "OPENAI_GENERATED_IMAGE_PUBLIC_URL_BASE",
    "http://nginx",
).rstrip("/")
OPENAI_RETRY_WITHOUT_IMAGE_ON_UPLOAD_ERROR = (
    os.getenv("OPENAI_RETRY_WITHOUT_IMAGE_ON_UPLOAD_ERROR", "1") == "1"
)

GOOGLE_SHEETS_PRODUCTS_RANGE = os.getenv("GOOGLE_SHEETS_PRODUCTS_RANGE", "A:I")



EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "1") == "1"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "schizzzox@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
