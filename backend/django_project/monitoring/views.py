from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.authentication import JWTAuthentication
from .models import MonitoredResource, Alert
from .serializers import MonitoredResourceSerializer, AlertSerializer
from .services import scan_existing_leaks


class MonitoredResourceListCreateView(generics.ListCreateAPIView):
    serializer_class = MonitoredResourceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MonitoredResource.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        resource = serializer.save(user=self.request.user)
        scan_existing_leaks(resource)


class AlertListView(generics.ListAPIView):
    serializer_class = AlertSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)
