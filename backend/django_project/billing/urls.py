from django.urls import path
from .views import InvoiceListView, PaymentListView, SubscriptionListView

urlpatterns = [
    path("invoices/", InvoiceListView.as_view(), name="invoice-list"),
    path("payments/", PaymentListView.as_view(), name="payment-list"),
    path(
        "subscriptions/",
        SubscriptionListView.as_view(),
        name="subscription-list"
    ),
]
