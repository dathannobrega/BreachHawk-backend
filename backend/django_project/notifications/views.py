from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from accounts.authentication import JWTAuthentication
from .models import SMTPConfig
from .serializers import SMTPConfigSerializer


class SMTPConfigView(generics.RetrieveUpdateAPIView):
    serializer_class = SMTPConfigSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get_object(self):
        obj, _ = SMTPConfig.objects.get_or_create(id=1)
        return obj
