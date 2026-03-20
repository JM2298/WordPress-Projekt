from django.urls import re_path

from .consumers import PingConsumer

websocket_urlpatterns = [
    re_path(r"ws/ping/$", PingConsumer.as_asgi()),
]
