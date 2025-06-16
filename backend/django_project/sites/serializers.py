from rest_framework import serializers
from .models import Site, TelegramAccount


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = [
            "id",
            "name",
            "links",
            "type",
            "auth_type",
            "captcha_type",
            "scraper",
            "needs_js",
            "bypass_config",
            "credentials",
        ]


class TelegramAccountSerializer(serializers.ModelSerializer):
    """Serializer for CRUD operations on Telegram accounts."""

    session_string = serializers.CharField(
        write_only=True, required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = TelegramAccount
        fields = ["id", "api_id", "api_hash", "session_string", "phone"]
        extra_kwargs = {"session_string": {"required": False}}