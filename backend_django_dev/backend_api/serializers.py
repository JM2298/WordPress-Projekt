from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        validate_password(attrs["password"])
        return attrs

    def validate_email(self, value: str) -> str:
        user_model = get_user_model()
        if value and user_model.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def create(self, validated_data: dict):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = get_user_model().objects.create_user(password=password, **validated_data)
        return user


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email"]


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class RegisterResponseSerializer(serializers.Serializer):
    user = UserPublicSerializer()
    tokens = TokenPairSerializer()


class PingSerializer(serializers.Serializer):
    service = serializers.CharField()
    status = serializers.CharField()


class SheetReadQuerySerializer(serializers.Serializer):
    range_name = serializers.CharField(
        required=False,
        default="Arkusz1!A1:D20",
        allow_blank=False,
    )


class SheetReadResponseSerializer(serializers.Serializer):
    rows = serializers.ListField(
        child=serializers.ListField(
            child=serializers.JSONField(),
            allow_empty=True,
        ),
        allow_empty=True,
    )


class SheetAppendRequestSerializer(serializers.Serializer):
    row = serializers.ListField(
        child=serializers.JSONField(),
        allow_empty=False,
    )
    range_name = serializers.CharField(
        required=False,
        default="Arkusz1!A:D",
        allow_blank=False,
    )


class SheetAppendResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    result = serializers.JSONField()
