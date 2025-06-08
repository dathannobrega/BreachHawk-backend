from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from accounts.authentication import JWTAuthentication
from .models import Site
from .serializers import SiteSerializer


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
