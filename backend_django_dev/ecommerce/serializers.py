from urllib.parse import urlsplit

from rest_framework import serializers


class CategoryImageSerializer(serializers.Serializer):
    src = serializers.URLField()


class CategoryCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    image = CategoryImageSerializer(required=False)


class ProductCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)


class ProductImageSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1, required=False)
    src = serializers.CharField(required=False)

    def validate_src(self, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"}:
            raise serializers.ValidationError("Image src must start with http or https.")
        if not parsed.netloc:
            raise serializers.ValidationError("Image src must include a host.")
        return value

    def validate(self, attrs: dict) -> dict:
        if "id" not in attrs and "src" not in attrs:
            raise serializers.ValidationError("Provide at least one of: id, src.")
        return attrs


class ProductCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    type = serializers.CharField(max_length=32)
    regular_price = serializers.CharField(max_length=32)
    description = serializers.CharField(required=False, allow_blank=True)
    short_description = serializers.CharField(required=False, allow_blank=True)
    categories = ProductCategorySerializer(many=True, required=False)
    images = ProductImageSerializer(many=True, required=False)
