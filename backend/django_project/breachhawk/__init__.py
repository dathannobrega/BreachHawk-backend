try:
    from .celery import app as celery_app
    __all__ = ["celery_app"]
except Exception:  # pragma: no cover - celery optional during tests
    celery_app = None
    __all__ = []
