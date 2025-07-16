from rest_framework import serializers
from .models import Site, SiteLink, TelegramAccount


class SiteLinkSerializer(serializers.ModelSerializer):
    """Serializer for handling site links."""

    class Meta:
        model = SiteLink
        fields = ["id", "url"]
        read_only_fields = ["id"]


class SiteSerializer(serializers.ModelSerializer):
    links = SiteLinkSerializer(many=True, required=False)

    class Meta:
        model = Site
        fields = [
            "id",
            "name",
            "url",
            "links",
            "type",
            "auth_type",
            "captcha_type",
            "scraper",
            "needs_js",
            "enabled",
            "bypass_config",
            "credentials",
            "telegram_account",
        ]

    def create(self, validated_data):
        links_data = validated_data.pop("links", [])
        site = Site.objects.create(**validated_data)
        for link in links_data:
            SiteLink.objects.create(site=site, **link)
        return site

    def update(self, instance, validated_data):
        links_data = validated_data.pop("links", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if links_data is not None:
            instance.links.all().delete()
            for link in links_data:
                SiteLink.objects.create(site=instance, **link)
        return instance


class TelegramAccountSerializer(serializers.ModelSerializer):
    """Serializer for CRUD operations on Telegram accounts."""

    session_string = serializers.CharField(
        write_only=True, required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = TelegramAccount
        fields = ["id", "api_id", "api_hash", "session_string", "phone"]
        extra_kwargs = {"session_string": {"required": False}}
