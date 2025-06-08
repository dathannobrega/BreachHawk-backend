from rest_framework import serializers
from .models import Site


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
