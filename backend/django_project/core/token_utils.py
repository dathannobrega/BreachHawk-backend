"""Token helpers using Django's signing utilities."""

from django.core import signing


def generate_unsubscribe_token(user_id: int) -> str:
    """Return a signed token carrying ``user_id``."""
    return signing.dumps({"user_id": user_id}, salt="unsubscribe-salt")


def verify_unsubscribe_token(token: str, max_age_seconds: int = 60 * 60 * 24 * 7) -> int:
    """Validate ``token`` and return the embedded ``user_id``."""
    data = signing.loads(token, max_age=max_age_seconds, salt="unsubscribe-salt")
    return data["user_id"]
