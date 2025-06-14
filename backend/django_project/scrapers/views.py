from rest_framework import viewsets
from accounts.authentication import JWTAuthentication
from accounts.permissions import IsAdminOrPlatformAdmin
from .models import ScrapeLog, Snapshot
from .serializers import ScrapeLogSerializer, SnapshotSerializer


class ScrapeLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScrapeLog.objects.all()
    serializer_class = ScrapeLogSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]


class SnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Snapshot.objects.all()
    serializer_class = SnapshotSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]
