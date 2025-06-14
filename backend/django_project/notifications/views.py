from rest_framework import generics
from accounts.authentication import JWTAuthentication
from accounts.permissions import IsAdminOrPlatformAdmin
from .models import SMTPConfig
from .serializers import SMTPConfigSerializer


class SMTPConfigView(generics.RetrieveUpdateAPIView):
    serializer_class = SMTPConfigSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]

    def get_object(self):
        obj, _ = SMTPConfig.objects.get_or_create(id=1)
        return obj
