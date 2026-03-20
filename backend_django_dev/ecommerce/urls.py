from django.urls import path

from .views import create_category, product_detail, products

urlpatterns = [
    path("categories/", create_category, name="ecommerce-category-create"),
    path("products/", products, name="ecommerce-products"),
    path("products/<int:product_id>/", product_detail, name="ecommerce-product-detail"),
]
