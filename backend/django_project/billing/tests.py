import pytest
from django.urls import reverse
from .models import Invoice, Payment, Subscription

@pytest.mark.django_db
def test_invoice_model_str():
    obj = Invoice.objects.create(stripe_id="inv_1", amount_due=100)
    assert str(obj) == "inv_1"


@pytest.mark.django_db
def test_payment_model_str():
    obj = Payment.objects.create(stripe_id="pay_1", amount=50, created=0)
    assert str(obj) == "pay_1"


@pytest.mark.django_db
def test_subscription_model_str():
    obj = Subscription.objects.create(stripe_id="sub_1")
    assert str(obj) == "sub_1"


@pytest.mark.django_db
def test_billing_api_empty_lists(auth_client):
    for name in ["invoice-list", "payment-list", "subscription-list"]:
        resp = auth_client.get(reverse(name))
        assert resp.status_code == 200
        assert resp.data == []
