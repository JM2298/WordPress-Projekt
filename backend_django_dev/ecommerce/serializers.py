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
    src = serializers.URLField(required=False)

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
