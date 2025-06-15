from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import JWTAuthentication
from accounts.permissions import IsAdminOrPlatformAdmin
from .models import SMTPConfig
from .serializers import SMTPConfigSerializer, TestEmailSerializer
from .email_utils import send_test_email


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


class SMTPTestEmailView(APIView):
    """Send a test email using the current SMTP configuration."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]

    def post(self, request):
        serializer = TestEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        to_email = serializer.validated_data["to_email"]
        try:
            send_test_email(to_email)
        except Exception as exc:  # pragma: no cover - network errors
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"success": True})
