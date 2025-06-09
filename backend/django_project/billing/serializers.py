from rest_framework import serializers
from .models import Invoice, Payment, Subscription


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "stripe_id",
            "customer",
            "amount_due",
            "status",
            "due_date",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "stripe_id", "amount", "status", "created"]


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            "id",
            "stripe_id",
            "customer",
            "status",
            "current_period_end",
        ]
