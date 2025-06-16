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
    class Meta:
        model = TelegramAccount
        fields = ["id", "api_id", "api_hash", "phone"]
