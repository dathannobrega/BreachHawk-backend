from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import JWTAuthentication
from accounts.permissions import IsAdminOrPlatformAdmin
from .service import (
    list_invoices,
    list_payments,
    list_subscriptions,
)


class InvoiceListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]

    def get(self, request):
        return Response(list_invoices())


class PaymentListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]

    def get(self, request):
        return Response(list_payments())


class SubscriptionListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]

    def get(self, request):
        return Response(list_subscriptions())
