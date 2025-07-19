from rest_framework import viewsets
from accounts.authentication import JWTAuthentication
from accounts.permissions import IsAdminOrPlatformAdmin
from breachhawk.celery import refresh_scraper_schedule
from .models import Site, TelegramAccount
from .serializers import SiteSerializer, TelegramAccountSerializer


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        refresh_scraper_schedule.delay()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        refresh_scraper_schedule.delay()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        refresh_scraper_schedule.delay()


class TelegramAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Telegram accounts."""

    queryset = TelegramAccount.objects.all()
    serializer_class = TelegramAccountSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]
