from rest_framework import viewsets, generics
from accounts.authentication import JWTAuthentication
from accounts.permissions import IsAdminOrPlatformAdmin, IsPlatformAdmin
from .models import Site, TelegramAccount
from .serializers import SiteSerializer, TelegramAccountSerializer


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]


class TelegramAccountListView(generics.ListAPIView):
    queryset = TelegramAccount.objects.all()
    serializer_class = TelegramAccountSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsPlatformAdmin]
