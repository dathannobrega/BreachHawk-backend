from rest_framework import serializers
from .models import SMTPConfig, Webhook


class SMTPConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTPConfig
        fields = ["id", "host", "port", "username", "from_email"]


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = ["id", "user", "url", "enabled"]
