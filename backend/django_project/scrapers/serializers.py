from rest_framework import serializers
from .models import ScrapeLog, Snapshot


class ScrapeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapeLog
        fields = ["id", "site", "url", "success", "message", "created_at"]


class SnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snapshot
        fields = ["id", "site", "taken_at", "screenshot", "html"]


class TaskResponseSerializer(serializers.Serializer):
    """Serializer for Celery task responses."""

    task_id = serializers.CharField()
    status = serializers.CharField()


class TaskStatusSerializer(TaskResponseSerializer):
    """Serializer including the result of a Celery task."""

    result = serializers.JSONField(required=False)
