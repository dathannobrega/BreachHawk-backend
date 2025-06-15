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
        obj = SMTPConfig.objects.first()
        if obj is None:
            from django.conf import settings

            obj = SMTPConfig.objects.create(
                host=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASS,
                from_email=settings.SMTP_USER,
            )
        return obj
