from rest_framework import serializers


class ProductGenerationRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=1000)
    type = serializers.CharField(max_length=32, required=False, default="simple")
    regular_price = serializers.CharField(
        max_length=32,
        required=False,
        allow_blank=True,
    )
    category_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
    )
