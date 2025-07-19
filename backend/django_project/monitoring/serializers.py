from rest_framework import serializers
from .models import MonitoredResource, Alert
from leaks.serializers import LeakSerializer


class MonitoredResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoredResource
        fields = ["id", "keyword", "created_at"]


class AlertSerializer(serializers.ModelSerializer):
    leak = LeakSerializer(read_only=True)

    class Meta:
        model = Alert
        fields = ["id", "resource", "leak", "created_at"]
