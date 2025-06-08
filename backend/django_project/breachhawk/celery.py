import os
from celery import Celery, states
from celery.exceptions import Ignore
from django.conf import settings
import structlog

from core.logging_conf import configure_logging
from scrapers.service import run_scraper_for_site
from sites.models import Site

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "breachhawk.settings")

configure_logging()
logger = structlog.get_logger(__name__)

app = Celery(
    "breachhawk",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
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
