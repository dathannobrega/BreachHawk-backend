from django.http import HttpRequest


def get_client_ip(request: HttpRequest) -> str:
    """Return client IP from a Django request."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    return ip
