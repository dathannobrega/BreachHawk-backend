from rest_framework import serializers
from .models import Site, SiteLink, TelegramAccount


class SiteLinkSerializer(serializers.ModelSerializer):
    """Serializer for handling site links."""

    id = serializers.IntegerField(required=False)

    class Meta:
        model = SiteLink
        fields = ["id", "url"]
        extra_kwargs = {"url": {"validators": []}}


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
        if not validated_data.get("url") and links_data:
            validated_data["url"] = links_data[0]["url"]
        site = Site.objects.create(**validated_data)
        for link in links_data:
            SiteLink.objects.create(site=site, **link)
        return site

    def update(self, instance, validated_data):
        links_data = validated_data.pop("links", None)
        if not validated_data.get("url") and links_data and not instance.url:
            validated_data["url"] = links_data[0]["url"]
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if links_data is not None:
            existing_ids = []
            for link in links_data:
                link_id = link.get("id")
                if link_id:
                    obj = instance.links.filter(id=link_id).first()
                    if obj:
                        url = link.get("url", obj.url)
                        obj.url = url
                        obj.save()
                        existing_ids.append(obj.id)
                        continue
                obj = SiteLink.objects.create(
                    site=instance,
                    url=link.get("url"),
                )
                existing_ids.append(obj.id)

            # remove links not present in the request
            instance.links.exclude(id__in=existing_ids).delete()
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
