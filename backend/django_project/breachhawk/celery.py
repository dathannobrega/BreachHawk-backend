"""Celery application configuration and task definitions."""

import os

import django
from celery import Celery, states
from celery.schedules import crontab
from celery.exceptions import Ignore
from django.conf import settings
import structlog

from core.logging_conf import configure_logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "breachhawk.settings")
django.setup()

from scrapers.service import run_scraper_for_site  # noqa: E402
from scrapers import load_custom_scrapers
from sites.models import Site  # noqa: E402

configure_logging()
logger = structlog.get_logger(__name__)


def refresh_site_schedules(celery_app: Celery) -> None:
    """Configure periodic tasks based on Site frequencies."""
    from celery.schedules import crontab

    celery_app.conf.beat_schedule = {}
    for site in Site.objects.filter(enabled=True):
        schedule = crontab(minute=f"*/{site.frequency_minutes}")
        celery_app.add_periodic_task(
            schedule,
            scrape_site.s({"siteId": site.id}),
            name=f"scrape_{site.id}",
        )


app = Celery(
    "breachhawk",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)


@app.task(name="refresh_scraper_schedule")
def refresh_scraper_schedule() -> None:
    """Refresh Celery beat schedule based on database values."""
    refresh_site_schedules(app)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    refresh_site_schedules(sender)
    sender.add_periodic_task(
        crontab(minute="*/1"),
        refresh_scraper_schedule.s(),
        name="refresh_schedule",
    )


def _fail(task, msg: str, exc_cls: str = "ValueError"):
    logger.error("Celery Failure", task_id=task.request.id, message=msg)
    task.update_state(
        state=states.FAILURE,
        meta={
            "exc_type": exc_cls,
            "exc_message": msg,
            "exc_module": "builtins",
        },
    )
    raise Ignore()


@app.task(bind=True, name="scrape_site")
def scrape_site(self, payload: dict) -> dict:
    site_id = payload.get("siteId") if isinstance(payload, dict) else payload
    try:
        inserted = run_scraper_for_site(site_id, payload)
        return {"inserted": inserted}
    except Exception as exc:
        logger.exception("Exception in scrape_site", error=str(exc))
        return _fail(self, str(exc), exc_cls=exc.__class__.__name__)


@app.task(name="scrape_all_sites")
def scrape_all_sites() -> int:
    total = 0
    for site in Site.objects.filter(enabled=True):
        total += run_scraper_for_site(site.id)
    return total


@app.task(name="reload_scrapers")
def reload_scrapers_task() -> bool:
    """Reload custom scrapers on all workers."""
    load_custom_scrapers()
    refresh_site_schedules(app)
    return True
