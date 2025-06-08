"""Wrapper helpers around the optional ``stripe`` dependency."""

from django.conf import settings

try:  # pragma: no cover - import-time check
    import stripe
except ModuleNotFoundError:  # package is optional
    stripe = None

if stripe:
    stripe.api_key = settings.STRIPE_API_KEY or ""


def list_invoices(limit: int = 20):
    if not stripe or not getattr(stripe, "api_key", None):
        return []
    try:
        resp = stripe.Invoice.list(limit=limit)
        return [inv.to_dict_recursive() for inv in resp.data]
    except Exception:
        return []


def list_payments(limit: int = 20):
    if not stripe or not getattr(stripe, "api_key", None):
        return []
    try:
        resp = stripe.PaymentIntent.list(limit=limit)
        return [p.to_dict_recursive() for p in resp.data]
    except Exception:
        return []


def list_subscriptions(limit: int = 20):
    if not stripe or not getattr(stripe, "api_key", None):
        return []
    try:
        resp = stripe.Subscription.list(limit=limit)
        return [s.to_dict_recursive() for s in resp.data]
    except Exception:
        return []
