from rest_framework import viewsets
from accounts.authentication import JWTAuthentication
from accounts.permissions import IsAdminOrPlatformAdmin
from .models import Site, TelegramAccount
from .serializers import SiteSerializer, TelegramAccountSerializer


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]


class TelegramAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Telegram accounts."""

    queryset = TelegramAccount.objects.all()
    serializer_class = TelegramAccountSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]
