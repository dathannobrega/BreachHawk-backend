from leaks.serializers import LeakSerializer
from rest_framework import serializers

from .models import Alert, MonitoredResource


class MonitoredResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoredResource
        fields = ["id", "keyword", "created_at"]


class AlertSerializer(serializers.ModelSerializer):
    leak = LeakSerializer(read_only=True)

    class Meta:
        model = Alert
        fields = ["id", "resource", "leak", "acknowledged", "created_at"]


class AlertAckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ["acknowledged"]
