from django.urls import path

from .views import generate_and_create_product

urlpatterns = [
    path(
        "products/generate-create/",
        generate_and_create_product,
        name="openai-generate-create-product",
    ),
]
