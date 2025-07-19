from accounts.authentication import JWTAuthentication
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import Alert, MonitoredResource
from .serializers import (
    AlertAckSerializer,
    AlertSerializer,
    MonitoredResourceSerializer,
)
from .services import scan_existing_leaks


class MonitoredResourceListCreateView(generics.ListCreateAPIView):
    serializer_class = MonitoredResourceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MonitoredResource.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        keyword = serializer.validated_data.get("keyword")
        qs = MonitoredResource.objects.filter(user=user, keyword=keyword)
        if qs.exists():
            raise ValidationError({"detail": "Recurso j\u00e1 monitorado."})
        resource = serializer.save(user=user)
        scan_existing_leaks(resource)


class MonitoredResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MonitoredResourceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MonitoredResource.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        user = self.request.user
        keyword = serializer.validated_data.get("keyword")
        if keyword:
            qs = MonitoredResource.objects.filter(user=user, keyword=keyword).exclude(
                pk=self.get_object().pk
            )
            if qs.exists():
                raise ValidationError({"detail": "Recurso j\u00e1 monitorado."})
        serializer.save()


class AlertListView(generics.ListAPIView):
    serializer_class = AlertSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)


class AlertAckView(generics.UpdateAPIView):
    serializer_class = AlertAckSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)
